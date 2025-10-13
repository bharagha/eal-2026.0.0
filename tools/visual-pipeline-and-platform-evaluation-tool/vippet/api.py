import logging
import yaml
import os

from typing import List
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from uuid import UUID

from gstpipeline import PipelineLoader, CustomGstPipeline
from optimize import PipelineOptimizer
from explore import GstInspector

import api_models as models
from pipelines.pipeline_page import download_file
from utils import prepare_video_and_constants
from device import DeviceDiscovery
from models import SupportedModelsManager
from benchmark import Benchmark


TEMP_DIR = "/tmp/"

with open("api/vippet.yaml") as f:
    openapi_schema = yaml.safe_load(f)

app = FastAPI(
    title="Visual Pipeline and Platform Evaluation Tool API",
    description="API for Visual Pipeline and Platform Evaluation Tool",
    version="1.0.0",
)
app.openapi = lambda: openapi_schema

gst_inspector = GstInspector()

@app.get("/pipelines", response_model=List[models.Pipeline])
def get_pipelines():
    pipeline_infos = []
    for pipeline in PipelineLoader.list():
        pipeline_gst, config = PipelineLoader.load(pipeline)
        pipeline_infos.append(models.Pipeline(
            id=pipeline,
            name=config.get("name", "Unnamed Pipeline"),
            version=config.get("version", "0.0.1"),
            description=config.get("definition", config.get("description", "")),
            type=models.PipelineType.GSTREAMER,
            parameters=models.PipelineParameters(
                default={
                    "launch_string": pipeline_gst.get_default_gst_launch(elements=gst_inspector.get_elements())
                }
            )
        ))
    return pipeline_infos

@app.post("/pipelines", status_code=201)
def create_pipeline(body: models.PipelineDefinition):
    """Create a custom pipeline from a GST launch string."""
    try:
        # Validate the GST string first
        is_valid, validation_message = CustomPipelineManager.validate_gst_string(body.launch_string)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid GST string: {validation_message}")

        pipeline, config = CustomPipelineManager.create_custom_pipeline(
            gst_launch_string=body.launch_string,
            name=body.name,
            description=body.description
        )

        # Return location header as per OpenAPI spec
        location = f"/pipelines/{body.name}/{body.version}"
        return JSONResponse(
            content={"message": "Pipeline created successfully"},
            status_code=201,
            headers={"Location": location}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create pipeline: {str(e)}")

@app.post("/pipelines/validate")
def validate_pipeline(body: models.PipelineValidation):
    """Validate a GST launch string pipeline."""
    is_valid, message = CustomPipelineManager.validate_gst_string(body.launch_string)
    if is_valid:
        return JSONResponse(content={"message": "Pipeline valid"}, status_code=200)
    else:
        raise HTTPException(status_code=400, detail=message)

@app.post("/pipelines/{name}/{version}/run")
def run_pipeline(
    name: str,
    version: str,
    body: models.PipelineRequestRun
):
    parameters = body.parameters or {}

    gst_pipeline, config = PipelineLoader.load_from_launch_string(parameters["launch_string"], name=name)

    # Download the pipeline recording files if using built-in config
    if "recording" in config:
        download_file(
            config["recording"]["url"],
            config["recording"]["filename"],
        )
        input_video_path = os.path.join(TEMP_DIR, config["recording"]["filename"])
    else:
        file_name = os.path.basename(body.source.uri)
        download_file(
            body.source.uri,
            file_name,
        )
        # Use the source URI from the request
        input_video_path = os.path.join(TEMP_DIR, file_name)


    recording_channels = 0
    inferencing_channels = parameters.get("inferencing_channels", 1)

    if recording_channels + inferencing_channels == 0:
        return {"error": "At least one channel must be enabled"}

    param_grid = {
        "live_preview_enabled": [False]
    }

    optimizer = PipelineOptimizer(
        pipeline=gst_pipeline,
        param_grid=param_grid,
        channels=(recording_channels, inferencing_channels),
        elements=gst_inspector.get_elements(),
    )

    optimizer.run_without_live_preview()

    best_result = optimizer.evaluate()
    if best_result is None:
        best_result_message = "No valid result was returned by the optimizer."
    else:
        best_result_message = (
            f"Total FPS: {best_result.total_fps:.2f}, "
            f"Per Stream FPS: {best_result.per_stream_fps:.2f}"
        )

    return best_result_message

@app.post("/pipelines/{name}/{version}/benchmark")
def benchmark_pipeline(
    name: str,
    version: str,
    body: models.PipelineRequestBenchmark
):
    dir = "smartnvr"  # This should be mapped from name/version in a real implementation
    gst_pipeline, config = PipelineLoader.load(dir)

    # Download the pipeline recording files if using built-in config
    if "recording" in config:
        download_file(
            config["recording"]["url"],
            config["recording"]["filename"],
        )
        input_video_path = os.path.join(TEMP_DIR, config["recording"]["filename"])
    else:
        file_name = os.path.basename(body.source.uri)
        download_file(
            body.source.uri,
            file_name,
        )
        # Use the source URI from the request
        input_video_path = os.path.join(TEMP_DIR, file_name)

    # Prepare parameters, ensuring input video is set
    parameters = body.parameters or {}
    parameters["input_video_player"] = input_video_path

    try:
        video_output_path, constants, param_grid = prepare_video_and_constants(**parameters)
    except ValueError as e:
        return {"error": str(e)}

    logging.info(f"Constants: {constants}")
    logging.info(f"param_grid: {param_grid}")

    # Initialize the benchmark class
    bm = Benchmark(
        pipeline_cls=gst_pipeline,
        fps_floor=parameters.get("fps_floor"),
        rate=parameters.get("ai_stream_rate"),
        parameters=param_grid,
        constants=constants,
        elements=gst_inspector.get_elements(),
    )

    # Run the benchmark
    s, ai, non_ai, fps = bm.run()

    # Return results
    try:
        result = config["parameters"]["benchmark"]["result_format"]
    except KeyError:
        result = (
            "Best Config: {s} streams ({ai} AI, {non_ai} non_AI) -> {fps:.2f} FPS"
        )

    return result.format(s=s, ai=ai, non_ai=non_ai, fps=fps)

@app.post("/pipelines/{name}/{version}/optimize")
def optimize_pipeline(name: str, version: str, request: models.PipelineRequestOptimize):
    return {"message": "Optimization started"}

@app.delete("/pipelines/{name}/{version}")
def delete_pipeline(name: str, version: str):
    return {"message": "Pipeline deleted"}

@app.get("/pipelines/status", response_model=List[models.PipelineInstanceStatus])
def get_pipeline_status():
    return []

@app.delete("/pipelines/{instance_id}", response_model=List[models.PipelineInstanceStatus])
def stop_pipeline_instance(instance_id: UUID):
    return []

@app.get("/pipelines/{instance_id}", response_model=models.PipelineInstanceSummary)
def get_pipeline_summary(instance_id: UUID):
    return models.PipelineInstanceSummary(id=0, type="type")

@app.get("/pipelines/{instance_id}/status", response_model=models.PipelineInstanceStatus)
def get_pipeline_instance_status(instance_id: UUID):
    return models.PipelineInstanceStatus(id=0, state="RUNNING")

@app.get("/devices", response_model=List[models.Device])
def get_devices():
    device_discovery = DeviceDiscovery()
    device_list = device_discovery.list_devices()
    return [
        models.Device(
            device_name=device.device_name,
            full_device_name=device.full_device_name,
            device_type=device.device_type.name if hasattr(device.device_type, 'name') else str(device.device_type),
            device_family=device.device_family.name if hasattr(device.device_family, 'name') else str(device.device_family),
            gpu_id=getattr(device, 'gpu_id', None)
        )
        for device in device_list
    ]

@app.get("/models", response_model=List[models.Model])
def get_models():
    models = SupportedModelsManager().get_all_available_models()
    return [
        models.Model(
            name=m.name,
            display_name=m.display_name,
            category=m.model_type,
            precision=m.display_name.split(" ")[-1].strip("()") if "(" in m.display_name else None
        )
        for m in models
    ]

@app.get("/metrics", response_model=List[models.MetricSample])
def get_metrics():
    return []
