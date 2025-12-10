# Usage

This guide covers how to use the Visual Pipeline and Platform Evaluation Tool to edit pipelines, run performance tests,
and execute density tests.

## Editing pipelines in Pipeline Builder

The Visual Pipeline and Platform Evaluation Tool provides a graphical interface for building and editing pipelines.
Pipeline parameters such as sources, models, and performance-related options can be inspected and modified graphically,
with changes propagated to the underlying configuration.

### Pipeline Import and Export

Pipelines can be imported from and exported to configuration files, enabling sharing of configurations between
environments and easier version control. Exported definitions capture both topology and key parameters, allowing
reproducible pipeline setups.

### Device Selection for Inference Elements

The Visual Pipeline and Platform Evaluation Tool (ViPPET) lets you select the `device` for inference elements such as
`gvadetect` and `gvaclassify`. However, in the current implementation there is no integrated mechanism to also update
the DLStreamer codec and post-processing elements for multi-GPU or mixed-device pipelines.

This means that:

- You can change the `device` property on AI elements (for example, to run detection on another GPU),
- But the corresponding DLStreamer elements for **decoding**, **post-processing**, and **encoding** may remain bound to
  a different GPU or to a default device.

In such cases a pipeline can:

- Fail to start,
- Error out during caps negotiation,
- Or run but produce an output video with no bounding boxes rendered, even though inference is executed.

The relevant DLStreamer elements include:

- **Decoder elements**, such as:
  - `vah264dec` (for GPU.0, or simply `GPU` on single-GPU systems)
  - `varenderD129h264dec` (for GPU.1)
  - `varenderD130h264dec` (for GPU.2)
- **Post-processing elements**, such as:
  - `vapostproc` (for GPU.0, or simply `GPU` on single-GPU systems)
  - `varenderD129postproc` (for GPU.1)
  - `varenderD130postproc` (for GPU.2)
- **Encoder elements**, such as:
  - `vah264enc`, `vah264lpenc` (for GPU.0, or simply `GPU` on single-GPU systems)
  - `varenderD129h264enc` (for GPU.1)
  - `varenderD130h264enc` (for GPU.2)

> **GPU.0 note:** In systems with only one GPU, it appears as just `GPU` and uses the generic elements above
> (`vah264dec`, `vapostproc`, `vah264enc`, `vah264lpenc`). Only on multi-GPU systems will elements for `GPU.1`,
> `GPU.2` etc. (`varenderD129*`, `varenderD130*`, etc.) appear.

#### Workaround

If you see that the pipeline fails or runs without expected bounding boxes:

1. Export or re-create the pipeline description.
2. Manually adjust the DLStreamer decoder, post-processing, and encoder elements so they are explicitly bound to the
   GPU/device consistent with the `device` used by `gvadetect` / `gvaclassify`.
3. Import this modified pipeline into ViPPET as a custom pipeline and run it with the corrected static device
   assignments.

Elements with suffixes like `D129`, `D130`, etc. are typically mapped to specific GPU indices (for example `GPU.1`,
`GPU.2`). The exact mapping between `varenderD129*` / `varenderD130*` elements and `GPU.X` devices depends on your
platform configuration and DLStreamer's GPU selection rules. For details on how these IDs map to GPU devices and how to
choose the correct elements for each GPU, see the DLStreamer documentation on GPU device selection: [GPU device
selection in
DLStreamer](https://docs.openedgeplatform.intel.com/2025.2/edge-ai-libraries/dl-streamer/dev_guide/gpu_device_selection.html).

### Using DLSOptimizer

When using the DLStreamer Optimizer (DLSOptimizer) from within ViPPET, optimization runs can be **long-running**:

- It may take **5-6 minutes** (or more, depending on pipeline complexity and hardware) for DLSOptimizer to explore
  variants and return an optimized pipeline.

In the current implementation, it can also happen that while DLSOptimizer is searching for an optimized pipeline, the
ViPPET application is **restarted**.

For more information about DLSOptimizer behavior and limitations, see the DLSOptimizer limitations section in the
DLStreamer repository: [DLSOptimizer
limitations](https://github.com/open-edge-platform/edge-ai-libraries/blob/release-2025.2.0/libraries/dl-streamer/scripts/optimizer/README.md#limitations).

#### Risks related to application restart during optimization

If ViPPET is restarted while DLSOptimizer is running:

- Any **in-progress optimization job** is interrupted and its results are lost.
- In the current release, an application restart **removes all user-created pipelines and all types of jobs** (tests,
  optimization runs, validation runs). Only predefined pipelines remain available after restart.
- You may need to **recreate or reimport** your custom pipelines and re-run your jobs after the application comes back.

#### Recommendations

- If this behavior is problematic in your environment (for example, it disrupts interactive work or automated
  workflows), avoid using pipeline optimization and instead:
  - Use baseline, hand-tuned pipelines.
  - Adjust parameters manually rather than relying on DLSOptimizer.

### Choosing the Encoding Device for "Save Output"

When you enable the **"Save output"** option in ViPPET:

- ViPPET records the output video to a file.
- You are asked to select a **device** that will be used for encoding.

The current implementation does not automatically infer the best encoding device from the existing pipeline. To avoid
confusion and potential issues, use the following guidelines.

#### How to choose the encoding device

- Prefer the **same device that is already used by the downstream video elements** in your pipeline.
- In most cases, the most reliable choice is:
  - The **device used by the element that is closest to the final `*sink`** in the pipeline (for example, the last
    `va*` encoder or post-processing element before a sink).
- Using a different device for encoding than the one used by the rest of the downstream path can:
  - Introduce unnecessary copies between devices,
  - Or, in some environments, cause pipeline negotiation or stability issues.

#### Mapping devices (`GPU.X`) to DLStreamer elements

DLStreamer maps logical GPU devices (`GPU.0`, `GPU.1`, `GPU.2`, …) to specific element variants as follows:

- **`GPU.0`** (or `GPU` in a single-GPU system) maps to the generic VA-API elements:
  - Decoders: `vah264dec`
  - Post-processing: `vapostproc`
  - Encoders: `vah264enc`, `vah264lpenc`
- **`GPU.1`, `GPU.2`, …** map to per-GPU elements whose names encode the GPU index, for example:
  - For `GPU.1`: elements like `varenderD129h264dec`, `varenderD129postproc`, `varenderD129h264enc`
  - For `GPU.2`: elements like `varenderD130h264dec`, `varenderD130postproc`, `varenderD130h264enc`
  - And so on for additional GPUs.

> **Note:** On systems with only one GPU, the device will be listed as simply `GPU` (not `GPU.0`) and you should always
> use the generic elements above (`vah264dec`, `vapostproc`, `vah264enc`, `vah264lpenc`).

#### Practical guidance

When selecting the encoding device in the **"Save output"** dialog:

- If your pipeline uses **`vah264dec` / `vapostproc` / `vah264enc` / `vah264lpenc`** near the end of the pipeline, it
  is typically running on **`GPU.0`** (or just `GPU` on a single-GPU system). → In this case, choose **`GPU.0`** (or
  `GPU`) for encoding.
- If your pipeline uses elements like **`varenderD129*`**, **`varenderD130*`**, etc. near the end of the pipeline,
  those typically correspond to **`GPU.1`**, **`GPU.2`**, and so on. → In this case, choose the `GPU.X` device that
  matches the `varenderDXXX*` elements used by the final encoder or post-processing stage.

For the precise and up-to-date mapping between `GPU.X` devices and `varenderDXXX*` elements on your platform, as well
as additional examples, see the DLStreamer GPU device selection guide: [GPU device selection in
DLStreamer](https://docs.openedgeplatform.intel.com/2025.2/edge-ai-libraries/dl-streamer/dev_guide/gpu_device_selection.html).

## Running performance tests

The Visual Pipeline and Platform Evaluation Tool enables performance testing of AI pipelines on Intel® hardware. Key
metrics such as CPU usage, GPU usage, and throughput can be collected and analyzed to optimize hardware selection.

### Current Limitations

- **NPU metrics are not visible in the UI**: ViPPET currently does not support displaying NPU-related metrics. NPU
  utilization, throughput, and latency are not exposed in the ViPPET UI.
- **Limited metrics in the ViPPET UI**: At this stage, the ViPPET UI shows only a limited set of metrics: current CPU
  utilization, current utilization of a single GPU, and the most recently measured FPS. More metrics (including
  timeline-based charts) are planned for future releases.
- **No live preview video for running pipelines**: Live preview of the video from a running pipeline is not supported
  in this release. As a workaround, you can enable the "Save output" option. After the pipeline finishes, inspect the
  generated output video file.

## Running density tests

Currently, it is recommended to run **a single operation at a time** from the following set: tests, optimization,
validation.

In this release:

- New jobs are **not rejected or queued** when another job is already running.
- Starting more than one job at the same time launches **multiple GStreamer instances**.
- This can significantly **distort performance results** (for example, CPU/GPU utilization and FPS).

For accurate and repeatable measurements, run these operations **one by one**.
