from gstpipeline import PipelineLoader
from api.api_schemas import PipelineType, Pipeline
from explore import GstInspector

gst_inspector = GstInspector()


class PipelineManager:
    def __init__(self):
        self.pipelines = self.load_predefined_pipelines()

    def add_pipeline(self, pipeline: Pipeline):
        if self.pipeline_exists(pipeline.name, pipeline.version):
            raise ValueError(
                f"Pipeline with name '{pipeline.name}' and version '{pipeline.version}' already exists."
            )
        self.pipelines.append(pipeline)

    def get_pipelines(self) -> list[Pipeline]:
        return self.pipelines

    def get_pipeline_by_name_and_version(self, name: str, version: str) -> Pipeline:
        pipeline = self._find_pipeline(name, version)
        if pipeline is not None:
            return pipeline
        raise ValueError(
            f"Pipeline with name '{name}' and version '{version}' not found."
        )

    def pipeline_exists(self, name: str, version: str) -> bool:
        return self._find_pipeline(name, version) is not None

    def _find_pipeline(self, name: str, version: str) -> Pipeline | None:
        for pipeline in self.pipelines:
            if pipeline.name == name and pipeline.version == version:
                return pipeline
        return None

    def load_predefined_pipelines(self):
        predefined_pipelines = []
        for pipeline_name in PipelineLoader.list():
            pipeline_gst, config = PipelineLoader.load(pipeline_name)
            predefined_pipelines.append(
                Pipeline(
                    name=config.get("name", "Unnamed Pipeline"),
                    version=config.get("version", "0.0.1"),
                    description=config.get("definition", ""),
                    type=PipelineType.GSTREAMER,
                    launch_string=pipeline_gst.get_default_gst_launch(
                        gst_inspector.get_elements()
                    ),
                    parameters=None,
                )
            )
        return predefined_pipelines
