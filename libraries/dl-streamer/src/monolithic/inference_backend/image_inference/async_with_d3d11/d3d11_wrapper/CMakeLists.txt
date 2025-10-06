# ==============================================================================
# Copyright (C) 2025 Intel Corporation
#
# SPDX-License-Identifier: MIT
# ==============================================================================

set (TARGET_NAME "d3d11_wrapper")

find_package(PkgConfig)


file (GLOB MAIN_SRC
        ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp
)

file (GLOB MAIN_HEADERS
        ${CMAKE_CURRENT_SOURCE_DIR}/*.h
)

add_library(${TARGET_NAME} STATIC ${MAIN_SRC} ${MAIN_HEADERS})
set_compile_flags(${TARGET_NAME})

target_include_directories(${TARGET_NAME}
PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${VA_INCLUDE_DIRS}
PRIVATE
        ${VADRM_INCLUDE_DIRS}
)

target_link_libraries(${TARGET_NAME}
PUBLIC
        logger
        pre_proc
        opencv_pre_proc
        utils
        d3d11
        dxgi
PRIVATE
        utils
)
