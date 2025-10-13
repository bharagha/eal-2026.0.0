from typing import Dict, Any, Optional
from fastapi import Body
from pydantic import BaseModel
from enum import Enum

# # Enums based on OpenAPI schema
class PipelineType(str, Enum):
    GSTREAMER = "GStreamer"

class PipelineInstanceState(str, Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    ABORTED = "ABORTED"

class SourceType(str, Enum):
    URI = "uri"
    GST = "gst"

# Define minimal models based on schema references
class Source(BaseModel):
    type: SourceType
    uri: Optional[str]

class PipelineParameters(BaseModel):
    default: Optional[Dict[str, Any]]

class Pipeline(BaseModel):
    id: str
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
    # TODO: Redefine after updating the OpenAPI schema
    async_: Optional[bool] = Body(default=True, alias="async")
    source: Source
    parameters: Optional[Dict[str, Any]]

class PipelineRequestBenchmark(BaseModel):
    # TODO: Redefine after updating the OpenAPI schema
    async_: Optional[bool] = Body(default=True, alias="async")

class PipelineRequestOptimize(BaseModel):
    # TODO: Redefine after updating the OpenAPI schema
    async_: Optional[bool] = Body(default=True, alias="async")

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
    device_type: str
    device_family: str
    gpu_id: Optional[int]

class Model(BaseModel):
    name: str
    display_name: str
    category: str
    precision: Optional[str]

class MetricSample(BaseModel):
    #TODO: redefine
    name: Optional[str]
    value: Optional[float]