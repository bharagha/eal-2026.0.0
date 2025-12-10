cmake_minimum_required(VERSION 3.5)

project(gstradarparse)


add_library(gstradarparse SHARED
    gstradarparse.cpp
)

target_include_directories(gstradarparse
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${GSTREAMER_INCLUDE_DIRS}
)

target_link_libraries(gstradarparse
    PRIVATE
        ${GSTREAMER_LIBRARIES}
        ${GSTVIDEO_LIBRARIES}
)

install(TARGETS gstradarparse
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}/gstreamer-1.0
)
