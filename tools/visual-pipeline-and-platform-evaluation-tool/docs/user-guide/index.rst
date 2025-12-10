Visual Pipeline and Platform Evaluation Tool
============================================

Assess Intel® hardware options, benchmark performance, and analyze key metrics to optimize hardware selection for AI
workloads.

Overview
########

The Visual Pipeline and Platform Evaluation Tool simplifies hardware selection for AI workloads by enabling
configuration of workload parameters, performance benchmarking, and analysis of key metrics such as throughput, CPU
usage, and GPU usage. With its intuitive interface, the tool provides actionable insights that support optimized
hardware selection and performance tuning.

Use Cases
#########

**Evaluating Hardware for AI Workloads**: Intel® hardware options can be assessed to balance cost, performance, and
efficiency. AI workloads can be benchmarked under real-world conditions by adjusting pipeline parameters and comparing
performance metrics.

**Performance Benchmarking for AI Models**: Model performance targets and KPIs can be validated by testing AI
inference pipelines with different accelerators to measure throughput, latency, and resource utilization.

Key Features
############

**Optimized for Intel® AI Edge Systems**: Pipelines can be run directly on target devices for seamless Intel® hardware
integration.

**Comprehensive Hardware Evaluation**: Metrics such as CPU frequency, GPU power usage, and memory utilization are
available for detailed analysis.

**Configurable AI Pipelines**: Parameters such as input channels, object detection models, and inference engines can be
adjusted to create tailored performance tests.

**Automated Video Generation**: Synthetic test videos can be generated to evaluate system performance under controlled
conditions.

How It Works
############

The Visual Pipeline and Platform Evaluation Tool integrates with AI-based video processing pipelines to support
hardware performance evaluation.

Workflow Overview
*****************

- **Data Ingestion**: Video streams from live cameras or recorded files are provided and pipeline parameters are
  configured to match evaluation needs.
- **AI Processing**: AI inference is applied using OpenVINO™ models to detect objects in the video streams.
- **Performance Evaluation**: Hardware performance metrics are collected, including CPU/GPU usage and power consumption.
- **Visualization & Analysis**: Real-time performance metrics are displayed on the dashboard to enable comparison of
  configurations and optimization of settings.

Disclaimers
###########

Video Generator Images
**********************

Intel provides six images for demo purposes only. You must provide your own images to run the video generator or to
create videos.

Human Rights
************

Intel is committed to respecting human rights and avoiding complicity in human rights abuses. See Intel's Global Human
Rights Principles. Intel's products and software are intended only to be used in applications that do not cause or
contribute to a violation of an internationally recognized human right.

Models Licensing
****************

`ssdlite_mobilenet_v2_INT8 <https://github.com/dlstreamer/pipeline-zoo-models/tree/main/storage/ssdlite_mobilenet_v2_INT8>`_
(Apache 2.0)

`resnet-50-tf_INT8 <https://github.com/dlstreamer/pipeline-zoo-models/tree/main/storage/resnet-50-tf_INT8>`_
(Apache 2.0)

`efficientnet-b0_INT8 <https://github.com/dlstreamer/pipeline-zoo-models/tree/main/storage/efficientnet-b0_INT8>`_
(Apache 2.0)

`yolov5s-416_INT8 <https://github.com/dlstreamer/pipeline-zoo-models/tree/main/storage/yolov5s-416_INT8>`_ (GPL v3)

Dataset Used: `Intel IoT DevKit Sample Videos <https://github.com/intel-iot-devkit/sample-videos?tab=readme-ov-file>`_
(CC-BY-4.0)*

Data Transparency
*****************

Refer to Model cards included in this folder for more information on the models and their usage in the Visual Pipeline
and Platform Evaluation tool.

Release Notes
#############

Details about the changes, improvements, and known issues in this release of the application.

Current Release: Version 2025.2.0
*********************************

**Release Date**: 2025-12-10

New Features (v2025.2.0)
^^^^^^^^^^^^^^^^^^^^^^^^

- **New graphical user interface (GUI)**: A visual representation of the underlying ``gst-launch`` pipeline graph is
  provided, presenting elements, links, and branches in an interactive view. Pipeline parameters (such as sources,
  models, and performance-related options) can be inspected and modified graphically, with changes propagated to the
  underlying configuration.
- **Pipeline import and export**: Pipelines can be imported from and exported to configuration files, enabling sharing
  of configurations between environments and easier version control. Exported definitions capture both topology and key
  parameters, allowing reproducible pipeline setups.
- **Backend and frontend separation**: The application is now structured as a separate backend and frontend, allowing
  independent development and deployment of each part. A fully functional REST API is exposed by the backend, which can
  be accessed directly by automation scripts or indirectly through the UI.
- **Extensible architecture for dynamic pipelines**: The internal architecture has been evolved to support dynamic
  registration and loading of pipelines. New pipeline types can be added without modifying core components, enabling
  easier experimentation with custom topologies.
- **POSE model support**: POSE estimation model is now supported as part of the pipeline configuration.
- **DLStreamer Optimizer integration**: Integration with the DLStreamer Optimizer has been added to simplify
  configuration of GStreamer-based pipelines. Optimized elements and parameters can be applied automatically, improving
  performance and reducing manual tuning.

Improvements (v2025.2.0)
^^^^^^^^^^^^^^^^^^^^^^^^

- **Model management enhancements**: Supported models can now be added and removed directly through the application.
  The model manager updates available models in a centralized configuration, ensuring that only selected models are
  downloaded, stored, and exposed in the UI and API.

Known Issues and Limitations (v2025.2.0)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Pipelines failing or missing bounding boxes when multiple devices/codecs are involved**: ViPPET lets you select the
  ``device`` for inference elements such as ``gvadetect`` and ``gvaclassify``. However, in the current implementation
  there is no integrated mechanism to also update the DLStreamer codec and post-processing elements for multi-GPU or
  mixed-device pipelines.
- **DLSOptimizer takes a long time or causes the application to restart**: When using DLSOptimizer from within ViPPET,
  optimization runs can be long-running. It may take 5-6 minutes (or more, depending on pipeline complexity and
  hardware) for DLSOptimizer to explore variants and return an optimized pipeline.
- **NPU metrics are not visible in the UI**: ViPPET currently does not support displaying NPU-related metrics.
- **Occasional "Connection lost" message in the UI**: The ViPPET UI may show a "Connection lost" message under
  transient network interruptions.
- **Application restart removes user-created pipelines and jobs**: In the current release, restarting the ViPPET
  application removes all pipelines created by the user, and all types of jobs.
- **Support limited to DLStreamer 2025.2.0 pipelines and models**: ViPPET currently supports only pipelines and models
  that are supported by DLStreamer 2025.2.0.
- **Limited metrics in the ViPPET UI**: At this stage, the ViPPET UI shows only a limited set of metrics.
- **Limited validation scope**: Validation and testing in this release focused mainly on sanity checks for predefined
  pipelines.
- **No live preview video for running pipelines**: Live preview of the video from a running pipeline is not supported
  in this release.
- **Recommended to run only one operation at a time**: Currently, it is recommended to run a single operation at a time.
- **Some GStreamer / DLStreamer elements may not be displayed correctly in the UI**: Some elements may not be displayed
  correctly by the ViPPET UI.
- **Supported models list is limited**: ViPPET currently supports only models defined in the configuration.
- **Pipelines cannot depend on files other than models or videos**: ViPPET does not support pipelines that require
  additional files beyond model files and video files.

Learn More
##########

- :doc:`Installation <./installation>`
- :doc:`Usage <./usage>`
- :doc:`API Reference <./api-reference>`

.. toctree::
   :hidden:
   :maxdepth: 2

   installation
   usage
   api-reference
   GitHub <https://github.com/open-edge-platform/edge-ai-libraries/tree/main/tools/visual-pipeline-and-platform-evaluation-tool>
