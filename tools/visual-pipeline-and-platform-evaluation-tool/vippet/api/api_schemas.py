from typing import Dict, Any, Optional
from fastapi import Body
from pydantic import BaseModel
from enum import Enum


# # Enums based on OpenAPI schema
class PipelineType(str, Enum):
    GSTREAMER = "GStreamer"
    FFMPEG = "FFmpeg"


class PipelineInstanceState(str, Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    ABORTED = "ABORTED"


class SourceType(str, Enum):
    URI = "uri"
    GST = "gst"


class DeviceType(str, Enum):
    DISCRETE = "DISCRETE"
    INTEGRATED = "INTEGRATED"


class DeviceFamily(str, Enum):
    CPU = "CPU"
    GPU = "GPU"
    NPU = "NPU"


# Define minimal models based on schema references
class Source(BaseModel):
    type: SourceType
    uri: Optional[str]


class PipelineParameters(BaseModel):
    default: Optional[Dict[str, Any]]


class Pipeline(BaseModel):
    name: str
    version: str
    description: str
    type: PipelineType
    parameters: Optional[PipelineParameters]


class PipelineDefinition(BaseModel):
    name: str
    version: str
    description: Optional[str]
    type: PipelineType
    launch_string: str
    parameters: Optional[PipelineParameters]


class PipelineValidation(BaseModel):
    type: PipelineType
    launch_string: str
    parameters: Optional[PipelineParameters]


class PipelineRequestRun(BaseModel):
    async_: Optional[bool] = Body(default=True, alias="async")
    source: Source
    parameters: Optional[Dict[str, Any]]
    tags: Optional[Dict[str, str]]


class PipelineRequestBenchmark(BaseModel):
    async_: Optional[bool] = Body(default=True, alias="async")
    source: Source
    parameters: Optional[Dict[str, Any]]
    tags: Optional[Dict[str, str]]


class PipelineRequestOptimize(BaseModel):
    async_: Optional[bool] = Body(default=True, alias="async")
    source: Source
    parameters: Optional[Dict[str, Any]]
    tags: Optional[Dict[str, str]]


class PipelineInstanceStatus(BaseModel):
    id: int
    start_time: int
    elapsed_time: int
    state: PipelineInstanceState
    total_fps: Optional[float]
    per_stream_fps: Optional[float]
    ai_streams: Optional[int]
    non_ai_streams: Optional[int]


class PipelineInstanceSummary(BaseModel):
    id: int
    request: PipelineRequestRun
    type: str


class Device(BaseModel):
    device_name: str
    full_device_name: str
    device_type: DeviceType
    device_family: DeviceFamily
    gpu_id: Optional[int]


class Model(BaseModel):
    name: str
    display_name: str
    category: str
    precision: Optional[str]


class MetricSample(BaseModel):
    name: str
    description: str
    timestamp: int
    value: float
