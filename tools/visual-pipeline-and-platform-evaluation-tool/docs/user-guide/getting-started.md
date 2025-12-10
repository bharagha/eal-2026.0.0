# Visual Pipeline and Platform Evaluation Tool

<!-- required for catalog, do not remove -->
Assess Intel® hardware options, benchmark performance, and analyze key metrics to optimize hardware selection for AI
workloads.

## Overview

The Visual Pipeline and Platform Evaluation Tool simplifies hardware selection for AI workloads by enabling
configuration of workload parameters, performance benchmarking, and analysis of key metrics such as throughput, CPU
usage, and GPU usage. With its intuitive interface, the tool provides actionable insights that support optimized
hardware selection and performance tuning.

### Use Cases

**Evaluating Hardware for AI Workloads**: Intel® hardware options can be assessed to balance cost, performance, and
efficiency. AI workloads can be benchmarked under real-world conditions by adjusting pipeline parameters and comparing
performance metrics.

**Performance Benchmarking for AI Models**: Model performance targets and KPIs can be validated by testing AI
inference pipelines with different accelerators to measure throughput, latency, and resource utilization.

### Key Features

**Optimized for Intel® AI Edge Systems**: Pipelines can be run directly on target devices for seamless Intel® hardware
integration.

**Comprehensive Hardware Evaluation**: Metrics such as CPU frequency, GPU power usage, and memory utilization are
available for detailed analysis.

**Configurable AI Pipelines**: Parameters such as input channels, object detection models, and inference engines can be
adjusted to create tailored performance tests.

**Automated Video Generation**: Synthetic test videos can be generated to evaluate system performance under controlled
conditions.

### How It Works

The Visual Pipeline and Platform Evaluation Tool integrates with AI-based video processing pipelines to support
hardware performance evaluation.

#### Workflow Overview

- **Data Ingestion**: Video streams from live cameras or recorded files are provided and pipeline parameters are
  configured to match evaluation needs.
- **AI Processing**: AI inference is applied using OpenVINO™ models to detect objects in the video streams.
- **Performance Evaluation**: Hardware performance metrics are collected, including CPU/GPU usage and power consumption.
- **Visualization & Analysis**: Real-time performance metrics are displayed on the dashboard to enable comparison of
  configurations and optimization of settings.

### Disclaimers

#### Video Generator Images

Intel provides six images for demo purposes only. You must provide your own images to run the video generator or to
create videos.

#### Human Rights

Intel is committed to respecting human rights and avoiding complicity in human rights abuses. See Intel's Global Human
Rights Principles. Intel's products and software are intended only to be used in applications that do not cause or
contribute to a violation of an internationally recognized human right.

#### Models Licensing

[ssdlite_mobilenet_v2_INT8](https://github.com/dlstreamer/pipeline-zoo-models/tree/main/storage/ssdlite_mobilenet_v2_INT8)
(Apache 2.0)

[resnet-50-tf_INT8](https://github.com/dlstreamer/pipeline-zoo-models/tree/main/storage/resnet-50-tf_INT8)
(Apache 2.0)

[efficientnet-b0_INT8](https://github.com/dlstreamer/pipeline-zoo-models/tree/main/storage/efficientnet-b0_INT8)
(Apache 2.0)

[yolov5s-416_INT8](https://github.com/dlstreamer/pipeline-zoo-models/tree/main/storage/yolov5s-416_INT8) (GPL v3)

Dataset Used: [Intel IoT DevKit Sample Videos](https://github.com/intel-iot-devkit/sample-videos?tab=readme-ov-file)
(CC-BY-4.0)*

#### Data Transparency

Refer to Model cards included in this folder for more information on the models and their usage in the Visual Pipeline
and Platform Evaluation tool.

## Release Notes

Details about the changes, improvements, and known issues in this release of the application.

### Current Release: Version 2025.2

**Release Date**: 2025-12-10

#### New Features (v2025.2)

- **New graphical user interface (GUI)**: A visual representation of the underlying `gst-launch` pipeline graph is
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

#### Improvements (v2025.2)

- **Model management enhancements**: Supported models can now be added and removed directly through the application.
  The model manager updates available models in a centralized configuration, ensuring that only selected models are
  downloaded, stored, and exposed in the UI and API.

#### Known Issues and Limitations (v2025.2)

- **Pipelines failing or missing bounding boxes when multiple devices/codecs are involved**: ViPPET lets you select the
  `device` for inference elements such as `gvadetect` and `gvaclassify`. However, in the current implementation there
  is no integrated mechanism to also update the DLStreamer codec and post-processing elements for multi-GPU or
  mixed-device pipelines. This means that you can change the `device` property on AI elements (for example, to run
  detection on another GPU), but the corresponding DLStreamer elements for decoding, post-processing, and encoding may
  remain bound to a different GPU or to a default device. In such cases a pipeline can fail to start, error out during
  caps negotiation, or run but produce an output video with no bounding boxes rendered, even though inference is
  executed.
- **DLSOptimizer takes a long time or causes the application to restart**: When using DLSOptimizer from within ViPPET,
  optimization runs can be long-running. It may take 5-6 minutes (or more, depending on pipeline complexity and
  hardware) for DLSOptimizer to explore variants and return an optimized pipeline. In the current implementation, it
  can also happen that while DLSOptimizer is searching for an optimized pipeline, the ViPPET application is restarted.
- **NPU metrics are not visible in the UI**: ViPPET currently does not support displaying NPU-related metrics. NPU
  utilization, throughput, and latency are not exposed in the ViPPET UI.
- **Occasional "Connection lost" message in the UI**: The ViPPET UI is a web application that communicates with backend
  services. Under transient network interruptions or short service unavailability, the UI may show a "Connection lost"
  message. If this message appears occasionally, refresh the browser page to re-establish the connection to the
  backend.
- **Application restart removes user-created pipelines and jobs**: In the current release, restarting the ViPPET
  application removes all pipelines created by the user, and all types of jobs (tests, optimization runs, validation
  runs, and similar). After a restart, only predefined pipelines remain available.
- **Support limited to DLStreamer 2025.2.0 pipelines and models**: ViPPET currently supports only pipelines and models
  that are supported by DLStreamer 2025.2.0. For the full list of supported models, elements, and other details, see
  the [DLStreamer release
  notes](https://github.com/open-edge-platform/edge-ai-libraries/blob/release-2025.2.0/libraries/dl-streamer/RELEASE_NOTES.md).
- **Limited metrics in the ViPPET UI**: At this stage, the ViPPET UI shows only a limited set of metrics: current CPU
  utilization, current utilization of a single GPU, and the most recently measured FPS.
- **Limited validation scope**: Validation and testing in this release focused mainly on sanity checks for predefined
  pipelines. For custom pipelines, their behavior in ViPPET is less explored and may vary. However, if a custom
  pipeline is supported and works correctly with DLStreamer 2025.2.0, it is expected to behave similarly when run via
  ViPPET.
- **No live preview video for running pipelines**: Live preview of the video from a running pipeline is not supported
  in this release. As a workaround, you can enable the "Save output" option. After the pipeline finishes, inspect the
  generated output video file.
- **Recommended to run only one operation at a time**: Currently, it is recommended to run a single operation at a time
  from the following set: tests, optimization, validation. In this release, new jobs are not rejected or queued when
  another job is already running. Starting more than one job at the same time launches multiple GStreamer instances.
  This can significantly distort performance results (for example, CPU/GPU utilization and FPS).
- **Some GStreamer / DLStreamer elements may not be displayed correctly in the UI**: Some GStreamer or DLStreamer
  elements used in a pipeline may not be displayed correctly by the ViPPET UI. Even if some elements are not shown as
  expected in the UI, the underlying pipeline is still expected to run.
- **Supported models list is limited and extending it is not guaranteed to work**: ViPPET currently supports only
  models defined in
  [supported_models.yaml](https://github.com/open-edge-platform/edge-ai-libraries/blob/release-2025.2.0/tools/visual-pipeline-and-platform-evaluation-tool/shared/models/supported_models.yaml).
  A user can try to extend this file with new models whose `source` is either `public` or `pipeline-zoo-models`, but
  there is no guarantee that such models will work out of the box.
- **Pipelines cannot depend on files other than models or videos**: Currently, ViPPET does not support pipelines that
  require additional files beyond model files and video files. Pipelines that depend on other external artifacts (for
  example, configuration files, custom resources, etc.) are not supported in this release.

### Version 1.2

**Release Date**: 2025-08-20

#### New Features (v1.2)

- **Feature 1**: Simple Video Structurization Pipeline: The Simple Video Structurization (D-T-C) pipeline is a
  versatile, use case-agnostic solution that supports license plate recognition, vehicle detection with attribute
  classification, and other object detection and classification tasks, adaptable based on the selected model.
- **Feature 2**: Live pipeline output preview: The pipeline now supports live output, allowing users to view real-time
  results directly in the UI. This feature enhances the user experience by providing immediate feedback on video
  processing tasks.
- **Feature 3**: New pre-trained models: The release includes new pre-trained models for object detection
  (`YOLO v8 License Plate Detector`) and classification (`PaddleOCR`, `Vehicle Attributes Recognition Barrier 0039`),
  expanding the range of supported use cases and improving accuracy for specific tasks.

#### Known Issues (v1.2)

- **Issue**: Metrics are displayed only for the last GPU when the system has multiple discrete GPUs.

### Version 1.0.0

**Release Date**: 2025-03-31

#### New Features (v1.0.0)

- **Feature 1**: Pre-trained Models Optimized for Specific Use Cases: Visual Pipeline and Platform Evaluation Tool
  includes pre-trained models that are optimized for specific use cases, such as object detection for Smart NVR
  pipeline. These models can be easily integrated into the pipeline, allowing users to quickly evaluate their
  performance on different Intel® platforms.
- **Feature 2**: Metrics Collection with Turbostat tool and Qmassa tool: Visual Pipeline and Platform Evaluation Tool
  collects real-time CPU and GPU performance metrics using Turbostat tool and Qmassa tool. The collector agent runs in
  a dedicated collector container, gathering CPU and GPU metrics. Users can access and analyze these metrics via
  intuitive UI, enabling efficient system monitoring and optimization.
- **Feature 3**: Smart NVR Pipeline Integration: The Smart NVR Proxy Pipeline is seamlessly integrated into the tool,
  providing a structured video recorder architecture. It enables video analytics by supporting AI inference on selected
  input channels while maintaining efficient media processing. The pipeline includes multi-view composition, media
  encoding, and metadata extraction for insights.

#### Known Issues (v1.0.0)

- **Issue**: The Visual Pipeline and Platform Evaluation Tool container fails to start the analysis when the "Run"
  button is clicked in the UI, specifically for systems without GPU.
  - **Workaround**: Consider upgrading the hardware to meet the required specifications for optimal performance.
