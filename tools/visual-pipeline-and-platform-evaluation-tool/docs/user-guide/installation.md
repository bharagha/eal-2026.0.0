# Installation

This guide covers installation and setup of the Visual Pipeline and Platform Evaluation Tool. Choose from Docker
Compose deployment or building from source, and learn how to configure your environment for optimal performance.

## Prerequisites

Before starting, ensure the following:

- **System requirements**: The system meets the minimum requirements specified below.
- **Docker platform**: Docker is installed. For details, see the
  [Docker installation guide](https://docs.docker.com/get-docker/).
- **Dependencies installed**:
  - **Git**: [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
  - **Make**: Standard build tool, typically provided by the `build-essential` (or equivalent) package on Linux.
  - **curl**: Command-line tool for transferring data with URLs, typically provided by the `curl` package on Linux.

For GPU and/or NPU usage, appropriate drivers must be installed. The recommended method is to use the DLS installation
script, which detects available devices and installs the required drivers. Follow the **Prerequisites** section in:

- [Install Guide Ubuntu –
  Prerequisites](https://github.com/open-edge-platform/edge-ai-libraries/blob/release-2025.2.0/libraries/dl-streamer/docs/source/get_started/install/install_guide_ubuntu.md#prerequisites)

This guide assumes basic familiarity with Git commands and terminal usage. For more information, see:

- [Git Documentation](https://git-scm.com/doc)

### Supported Platforms

#### Operating Systems

- Ubuntu 24.04.1 LTS

### Minimum Requirements

| **Component**       | **Minimum**                     | **Recommended**                      |
|---------------------|---------------------------------|--------------------------------------|
| **Processor**       | 11th Gen Intel® Core™ Processor | Intel® Core™ Ultra 7 Processor 155H  |
| **Memory**          | 8 GB                            | 8 GB                                 |
| **Disk Space**      | 256 GB SSD                      | 256 GB SSD                           |
| **GPU/Accelerator** | Intel® UHD Graphics             | Intel® Arc™ Graphics                 |

### Software Requirements

- Docker Engine version 20.10 or higher.
- For GPU and/or NPU usage, appropriate drivers must be installed. The recommended method is to use the DLS
  installation script, which detects available devices and installs the required drivers. Follow the
  **Prerequisites** section in: [Install Guide Ubuntu –
  Prerequisites](https://github.com/open-edge-platform/edge-ai-libraries/blob/release-2025.2.0/libraries/dl-streamer/docs/source/get_started/install/install_guide_ubuntu.md#prerequisites)

### Compatibility Notes

**Known Limitations**:

- GPU compute engine utilization metrics require Intel® Graphics.

## Option 1: Docker Compose Deployment

The **Visual Pipeline and Platform Evaluation Tool** helps hardware decision-makers and software developers select the
optimal Intel® platform by adjusting workload parameters and analyzing performance metrics. Through an intuitive
web-based interface, the Smart NVR pipeline can be executed and key metrics such as throughput and CPU/GPU utilization
can be evaluated to assess platform performance and determine appropriate system sizing.

By following this guide, the following tasks can be completed:

- **Set up the sample application**: Use the Docker Compose tool to quickly deploy the application in a target
  environment.
- **Run a predefined pipeline**: Execute the Smart NVR pipeline and observe metrics.

### Set up and First Use

1. **Set up the working directory**:

   ```bash
   mkdir -p visual-pipeline-and-platform-evaluation-tool/models
   mkdir -p visual-pipeline-and-platform-evaluation-tool/shared/models
   mkdir -p visual-pipeline-and-platform-evaluation-tool/shared/videos
   cd visual-pipeline-and-platform-evaluation-tool
   ```

2. **Download all required files**:

   ```bash
   curl -LO "https://github.com/open-edge-platform/edge-ai-libraries/raw/refs/heads/release-2025.2.0/tools/visual-pipeline-and-platform-evaluation-tool/setup_env.sh"
   curl -LO "https://github.com/open-edge-platform/edge-ai-libraries/raw/refs/heads/release-2025.2.0/tools/visual-pipeline-and-platform-evaluation-tool/compose.yml"
   curl -LO "https://github.com/open-edge-platform/edge-ai-libraries/raw/refs/heads/release-2025.2.0/tools/visual-pipeline-and-platform-evaluation-tool/compose.cpu.yml"
   curl -LO "https://github.com/open-edge-platform/edge-ai-libraries/raw/refs/heads/release-2025.2.0/tools/visual-pipeline-and-platform-evaluation-tool/compose.gpu.yml"
   curl -LO "https://github.com/open-edge-platform/edge-ai-libraries/raw/refs/heads/release-2025.2.0/tools/visual-pipeline-and-platform-evaluation-tool/compose.npu.yml"
   curl -LO "https://github.com/open-edge-platform/edge-ai-libraries/raw/refs/heads/release-2025.2.0/tools/visual-pipeline-and-platform-evaluation-tool/Makefile"
   curl -Lo models/Dockerfile "https://github.com/open-edge-platform/edge-ai-libraries/raw/refs/heads/release-2025.2.0/tools/visual-pipeline-and-platform-evaluation-tool/models/Dockerfile"
   curl -Lo models/model_manager.sh "https://github.com/open-edge-platform/edge-ai-libraries/raw/refs/heads/release-2025.2.0/tools/visual-pipeline-and-platform-evaluation-tool/models/model_manager.sh"
   curl -Lo shared/videos/default_recordings.yaml "https://github.com/open-edge-platform/edge-ai-libraries/raw/refs/heads/release-2025.2.0/tools/visual-pipeline-and-platform-evaluation-tool/shared/videos/default_recordings.yaml"
   curl -Lo shared/models/supported_models.yaml "https://github.com/open-edge-platform/edge-ai-libraries/raw/refs/heads/release-2025.2.0/tools/visual-pipeline-and-platform-evaluation-tool/shared/models/supported_models.yaml"
   chmod +x models/model_manager.sh
   chmod +x setup_env.sh
   ```

3. **Start the application**:

   ```bash
   make build-models run
   ```

4. **Verify that the application is running**:

   ```bash
   docker compose ps
   ```

5. Access the application UI:

   - Open a browser and go to `http://<IP>:<PORT>` (e.g. http://localhost if the default port is used).

### Validation

1. **Verify build success**:
   - Check the logs and look for confirmation messages indicating that the microservice has started successfully.

### Model Installation and Management

When the Visual Pipeline and Platform Evaluation Tool is launched for the first time, a prompt is displayed to select
and install the models to be used. This step allows installation of only the models relevant to the intended pipelines.

To manage the installed models again, run the following command:

```bash
make install-models-force
```

## Option 2: Building from source

Build the Visual Pipeline and Platform Evaluation Tool from source to customize, debug, or extend its functionality. In
this guide, the following tasks are covered:

- Setting up the development environment.
- Compiling the source code and resolving dependencies.
- Generating a runnable build for local testing or deployment.

This guide is intended for developers working directly with the source code.

### Steps to Build

1. **Clone the repository**:

   ```bash
   git clone https://github.com/open-edge-platform/edge-ai-libraries.git
   cd ./edge-ai-libraries/tools/visual-pipeline-and-platform-evaluation-tool
   ```

2. **Build and start the application**:

   ```bash
   make build run
   ```

### Validation

1. **Verify build success**:
   - Logs should be checked for confirmation messages indicating that the microservice has started successfully.
2. **Access the application UI**:
   - Open a browser and go to `http://<IP>:<PORT> (e.g. http://localhost if the default port is used).

## Optional: Building Video Generator

The Visual Pipeline and Platform Evaluation Tool includes a video generator that creates composite videos from images
stored in subdirectories.

This guide is intended for developers working directly with the source code.

**Build and start the tool**:

```bash
make run-videogenerator
```

### Make Changes

1. **Change input images**:

   Custom images can be used instead of the default sample images as follows:

   - Navigate to the `images` folder and create subfolders for new image categories, then place the relevant images
     inside those subfolders.
   - Open the `config.json` file located at `video_generator/config.json`.
   - Update the `object_counts` section to reference the new image folders. Existing categories (for example, `cars` or
     `persons`) should be replaced with the names of the new categories defined in the `images` folder:

     ```json
     {
        "background_file": "/usr/src/app/background.gif",
        "base_image_dir": "/usr/src/app/images",
        "output_file": "output_file",
        "target_resolution": [1920, 1080],
        "frame_count": 300,
        "frame_rate": 30,
        "swap_percentage": 20,
        "object_counts": {
           "cars": 3,
           "persons": 3
        },
        "object_rotation_rate": 0.25,
        "object_scale_rate": 0.25,
        "object_scale_range": [0.25, 1],
        "encoding": "H264",
        "bitrate": 20000,
        "swap_rate": 1
     }
     ```

2. **Configure parameters**:

   The program uses a `config.json` file to customize the video generation process. Below is an example configuration:

   ```json
   {
      "background_file": "/usr/src/app/background.gif",
      "base_image_dir": "/usr/src/app/images",
      "output_file": "output_file",
      "target_resolution": [1920, 1080],
      "frame_count": 300,
      "frame_rate": 30,
      "swap_percentage": 20,
      "object_counts": {
         "cars": 3,
         "persons": 3
      },
      "object_rotation_rate": 0.25,
      "object_scale_rate": 0.25,
      "object_scale_range": [0.25, 1],
      "encoding": "H264",
      "bitrate": 20000,
      "swap_rate": 1
   }
   ```

   Parameters in the `config.json` file can be configured as follows:

   - **`background_file`**: Path to a background image (GIF, PNG, and so on) used in composite frames.
   - **`base_image_dir`**: Path to the root directory containing categorized image subdirectories.
   - **`output_file`**: Base name for the generated video file. It is recommended not to provide a file extension and
     not to include `.` in the filename (for example, `output_file`).
   - **`target_resolution`**: Resolution of the output video in `[width, height]` format.
   - **`duration`**: Total duration of the generated video in seconds.
   - **`frame_count`**: Total number of frames in the generated video.
   - **`swap_percentage`**: Percentage of images that are swapped between frames.
   - **`object_counts`**: Dictionary specifying the number of images per category in each frame.
   - **`object_rotation_rate`**: Rate at which objects rotate per frame (for example, `0.25` means a quarter rotation
     per frame).
   - **`object_scale_rate`**: Rate at which the size of objects changes per frame (for example, `0.25` means the object
     size changes by 25% per frame).
   - **`object_scale_range`**: List specifying the minimum and maximum scale factors for the objects (for example,
     `[0.25, 1]` means objects can scale between 25% and 100% of their original size).
   - **`encoding`**: Video encoding format (for example, `H264`).
   - **`bitrate`**: Bitrate for video encoding, measured in kbps.
   - **`swap_interval`**: Frequency of image swapping within frames, in seconds.
   - **Supported encodings and video formats**:

     | **Encoding** | **Video Format** |
     |--------------|------------------|
     | **H264**     | .mp4             |
     | **HEVC**     | .mp4             |
     | **VP8**      | .webm            |
     | **VP9**      | .webm            |
     | **AV1**      | .mkv             |
     | **MPEG4**    | .avi             |
     | **ProRes**   | .mov             |
     | **Theora**   | .ogg             |

### Validation

1. **Verify build success**:
   - Logs should be checked for confirmation messages indicating that the microservice started successfully:

     ```bash
     docker compose logs videogenerator -f
     ```

   - Expected result: An MP4 file is created under the `shared/videos/video-generator` folder.

## Installation troubleshooting

### Application containers fail to start

In some environments, ViPPET services may fail to start correctly and the UI may not be reachable.

#### Troubleshooting steps

- Check container logs:

  ```bash
  docker compose logs
  ```

- Restart the stack using the provided Makefile:

  ```bash
  make stop run
  ```

This stops currently running containers and starts them again with the default configuration.

### Port conflicts for `vippet-ui`

If the `vippet-ui` service cannot be accessed in the browser, it may be caused by a port conflict on the host.

#### Troubleshooting steps

- In the Compose file (`compose.yml`), find the `vippet-ui` service and its `ports` section:

  ```yaml
  services:
    vippet-ui:
      ports:
        - "80:80"
  ```

- Change the **host port** (left side) to an available one, for example:

  ```yaml
  services:
    vippet-ui:
      ports:
        - "8081:80"
  ```

- Restart the stack and access ViPPET using the new port, e.g. `http://localhost:8081`.

## Supporting Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
