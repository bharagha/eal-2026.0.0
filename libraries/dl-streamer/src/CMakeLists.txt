# ==============================================================================
# Copyright (C) 2021-2025 Intel Corporation
#
# SPDX-License-Identifier: MIT
# ==============================================================================

#add_subdirectory(ffmpeg)
add_subdirectory(utils)

if(ENABLE_ARCHITECTURE_2_0)
    # Full set of components
    add_subdirectory(base)
    add_subdirectory(cpu)
    add_subdirectory(gst)
    add_subdirectory(opencl)
    add_subdirectory(opencv)
    add_subdirectory(openvino)
    add_subdirectory(sycl)
    add_subdirectory(vaapi)
else()
    # Subset of components
    add_subdirectory(base/dlstreamer_logger)
    add_subdirectory(gst/bins/model_proc)
    add_subdirectory(gst/metadata)
    add_subdirectory(gst/tracers/buffer_tracer)
    add_subdirectory(gst/tracers/latency_tracer)
endif()
