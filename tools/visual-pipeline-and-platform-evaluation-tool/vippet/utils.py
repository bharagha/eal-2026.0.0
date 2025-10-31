import logging
import os
import random
import re
import requests
import select
import string
import subprocess
from subprocess import Popen, PIPE
from typing import Any

import cv2
import psutil as ps

from gstpipeline import GstPipeline

cancelled = False
logger = logging.getLogger("utils")

TEMP_DIR = "/tmp/"
UINT8_DTYPE_SIZE = 1
DEFAULT_FRAME_RATE = 30.0
VIDEO_STREAM_META_PATH = "/tmp/shared_memory/video_stream.meta"

# Path to the directory where models are stored
MODELS_PATH = os.environ.get("MODELS_PATH", "/models/output")

# Path to the FPS file
FPS_FILE_PATH = "/home/dlstreamer/vippet/.collector-signals/fps.txt"


def prepare_video_and_constants(
    **kwargs: dict[str, Any],
):
    """
    Prepares the video output path, constants, and parameter grid for the pipeline.

    Args:
        input_video_player (str): Path to the input video.
        object_detection_model (str): Selected object detection model.
        object_detection_device (str): Selected object detection device.

    Returns:
        tuple: A tuple containing video_output_path, constants, and param_grid.
    """

    # Collect parameters from kwargs
    input_video_player = str(kwargs.get("input_video_player", ""))
    object_detection_model = kwargs.get("object_detection_model", "")
    object_detection_device = str(kwargs.get("object_detection_device", ""))
    object_detection_batch_size = kwargs.get("object_detection_batch_size", 1)
    object_detection_inference_interval = kwargs.get(
        "object_detection_inference_interval", 0.0
    )
    object_detection_nireq = kwargs.get("object_detection_nireq", 1)
    object_classification_model = kwargs.get("object_classification_model", "")
    object_classification_device = str(kwargs.get("object_classification_device", ""))
    object_classification_batch_size = kwargs.get("object_classification_batch_size", 1)
    object_classification_inference_interval = kwargs.get(
        "object_classification_inference_interval", 0.0
    )
    object_classification_reclassify_interval = kwargs.get(
        "object_classification_reclassify_interval", 0.0
    )
    object_classification_nireq = kwargs.get("object_classification_nireq", 1)
    tracking_type = kwargs.get("tracking_type", "short-term-imageless")
    pipeline_watermark_enabled = kwargs.get("pipeline_watermark_enabled", True)
    pipeline_video_enabled = kwargs.get("pipeline_video_enabled", True)

    random_string = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    video_output_path = input_video_player.replace(
        ".mp4", f"-output-{random_string}.mp4"
    )
    # Delete the video in the output folder before producing a new one
    # Otherwise, gstreamer will just save a few seconds of the video
    # and stop.
    if os.path.exists(video_output_path):
        os.remove(video_output_path)

    # Discover the video codec of the input video
    input_video_codec = discover_video_codec(input_video_player)
    if input_video_codec == "unknown":
        raise ValueError(
            "Could not detect the video codec of the input file. Please provide a valid video file."
        )
    if input_video_codec not in ["h264", "h265"]:
        raise ValueError(
            f"Input video codec '{input_video_codec}' is not supported. Please use a video with H.264 or H.265 codec."
        )

    # Reset the FPS file
    with open(FPS_FILE_PATH, "w") as f:
        f.write("0.0\n")

    param_grid = {
        "object_detection_device": object_detection_device.split(", "),
        "object_detection_batch_size": [object_detection_batch_size],
        "object_detection_inference_interval": [object_detection_inference_interval],
        "object_detection_nireq": [object_detection_nireq],
        "object_classification_device": object_classification_device.split(", "),
        "object_classification_batch_size": [object_classification_batch_size],
        "object_classification_inference_interval": [
            object_classification_inference_interval
        ],
        "object_classification_reclassify_interval": [
            object_classification_reclassify_interval
        ],
        "object_classification_nireq": [object_classification_nireq],
        "tracking_type": [tracking_type],
        "pipeline_watermark_enabled": [pipeline_watermark_enabled],
        "pipeline_video_enabled": [pipeline_video_enabled],
    }

    constants = {
        "VIDEO_PATH": input_video_player,
        "VIDEO_CODEC": input_video_codec,
        "VIDEO_OUTPUT_PATH": video_output_path,
    }

    # Validate and set object detection model path/proc
    if not is_model_supported_on_device(
        str(object_detection_model), str(object_detection_device)
    ):
        raise ValueError(
            f"Object Detection Model '{object_detection_model}' is not supported on device '{object_detection_device}'. Please select a different model or device."
        )
    (
        constants["OBJECT_DETECTION_MODEL_PATH"],
        constants["OBJECT_DETECTION_MODEL_PROC"],
    ) = get_model_path_and_proc(str(object_detection_model))

    # Validate and set object classification model path/proc
    if not is_model_supported_on_device(
        str(object_classification_model), str(object_classification_device)
    ):
        raise ValueError(
            f"Object Classification Model '{object_classification_model}' is not supported on device '{object_classification_device}'. Please select a different model or device."
        )
    (
        constants["OBJECT_CLASSIFICATION_MODEL_PATH"],
        constants["OBJECT_CLASSIFICATION_MODEL_PROC"],
    ) = get_model_path_and_proc(str(object_classification_model))

    return video_output_path, constants, param_grid


def is_model_supported_on_device(model_name: str, device: str) -> bool:
    # Models that are not supported on NPU
    npu_unsupported = {
        "YOLO v10s 640x640 (FP16)",
        "YOLO v10m 640x640 (FP16)",
        "YOLO v8 License Plate Detector (FP32)",
        "EfficientNet B0 (INT8)",
    }
    if model_name in npu_unsupported and device == "NPU":
        return False
    return True


def get_model_path_and_proc(model_name: str) -> tuple[str, str]:
    model_map = {
        "Disabled": ("Disabled", "Disabled"),
        "SSDLite MobileNet V2 (INT8)": (
            f"{MODELS_PATH}/pipeline-zoo-models/ssdlite_mobilenet_v2_INT8/FP16-INT8/ssdlite_mobilenet_v2.xml",
            f"{MODELS_PATH}/pipeline-zoo-models/ssdlite_mobilenet_v2_INT8/ssdlite_mobilenet_v2.json",
        ),
        "YOLO v5m 416x416 (INT8)": (
            f"{MODELS_PATH}/pipeline-zoo-models/yolov5m-416_INT8/FP16-INT8/yolov5m-416_INT8.xml",
            f"{MODELS_PATH}/pipeline-zoo-models/yolov5m-416_INT8/yolo-v5.json",
        ),
        "YOLO v5m 640x640 (INT8)": (
            f"{MODELS_PATH}/pipeline-zoo-models/yolov5m-640_INT8/FP16-INT8/yolov5m-640_INT8.xml",
            f"{MODELS_PATH}/pipeline-zoo-models/yolov5m-640_INT8/yolo-v5.json",
        ),
        "YOLO v5s 416x416 (INT8)": (
            f"{MODELS_PATH}/pipeline-zoo-models/yolov5s-416_INT8/FP16-INT8/yolov5s.xml",
            f"{MODELS_PATH}/pipeline-zoo-models/yolov5s-416_INT8/yolo-v5.json",
        ),
        "YOLO v10s 640x640 (FP16)": (
            f"{MODELS_PATH}/public/yolov10s/FP16/yolov10s.xml",
            "",
        ),
        "YOLO v10m 640x640 (FP16)": (
            f"{MODELS_PATH}/public/yolov10m/FP16/yolov10m.xml",
            "",
        ),
        "YOLO v8 License Plate Detector (FP32)": (
            f"{MODELS_PATH}/public/yolov8_license_plate_detector/FP32/yolov8_license_plate_detector.xml",
            "",
        ),
        "ResNet-50 TF (INT8)": (
            f"{MODELS_PATH}/pipeline-zoo-models/resnet-50-tf_INT8/resnet-50-tf_i8.xml",
            f"{MODELS_PATH}/pipeline-zoo-models/resnet-50-tf_INT8/resnet-50-tf_i8.json",
        ),
        "EfficientNet B0 (INT8)": (
            f"{MODELS_PATH}/pipeline-zoo-models/efficientnet-b0_INT8/FP16-INT8/efficientnet-b0.xml",
            f"{MODELS_PATH}/pipeline-zoo-models/efficientnet-b0_INT8/efficientnet-b0.json",
        ),
        "MobileNet V2 PyTorch (FP16)": (
            f"{MODELS_PATH}/omz/mobilenet-v2-pytorch/FP16/mobilenet-v2-pytorch.xml",
            f"{MODELS_PATH}/omz/mobilenet-v2-pytorch/mobilenet-v2.json",
        ),
        "PaddleOCR (FP32)": (
            f"{MODELS_PATH}/public/ch_PP-OCRv4_rec_infer/FP32/ch_PP-OCRv4_rec_infer.xml",
            "",
        ),
        "Vehicle Attributes Recognition Barrier 0039 (FP16)": (
            f"{MODELS_PATH}/omz/vehicle-attributes-recognition-barrier-0039/FP16/vehicle-attributes-recognition-barrier-0039.xml",
            f"{MODELS_PATH}/omz/vehicle-attributes-recognition-barrier-0039/vehicle-attributes-recognition-barrier-0039.json",
        ),
    }
    if model_name not in model_map:
        raise ValueError("Unrecognized model name")
    return model_map[model_name]


def is_yolov10_model(model_path: str) -> bool:
    """
    Checks if the given model path corresponds to a YOLO v10 model.

    Args:
        model_path (str): Path to the model file.

    Returns:
        bool: True if the model is a YOLO v10 model, False otherwise.
    """
    return "yolov10" in model_path.lower()


def download_file(url, local_filename):
    file_path = os.path.join(TEMP_DIR, local_filename)
    if os.path.exists(file_path):
        logger.info(f"File {file_path} already exists, skipping download.")
        return file_path

    # Send a GET request to the URL
    with requests.get(url, stream=True) as response:
        response.raise_for_status()  # Check if the request was successful
        # Open a local file with write-binary mode
        with open(os.path.join(TEMP_DIR, local_filename), "wb") as file:
            # Iterate over the response content in chunks
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)  # Write each chunk to the local file
    return file_path


def discover_video_codec(video_path: str) -> str:
    """
    Discovers the codec for the given video file.

    Args:
        video_path (str): Path to the video file.

    Returns:
        str: Video codec name (e.g., 'h264', 'h265', etc.).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video file: {video_path}")
        return "unknown"
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    cap.release()
    # Decode the FOURCC integer into a 4-character string by extracting each byte.
    video_codec = (
        "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)]).strip().lower()
    )
    if "avc" in video_codec:
        return "h264"
    if "hevc" in video_codec:
        return "h265"
    return video_codec or "unknown"


def replace_file_path(launch_string: str, file_path: str) -> str:
    # Replace after 'filesrc location='
    launch_string = re.sub(
        r"(filesrc\s+location=)[^\s!]+", rf"\1{file_path}", launch_string
    )
    # Replace after 'source='
    launch_string = re.sub(r"(source=)[^\s!]+", rf"\1{file_path}", launch_string)
    return launch_string
