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

## Learn More

- [Installation](docs/user-guide/installation.md)
- [Usage](docs/user-guide/usage.md)
- [Release Notes](docs/user-guide/getting-started.md#release-notes)
- [API Reference](docs/user-guide/api-reference.md)
