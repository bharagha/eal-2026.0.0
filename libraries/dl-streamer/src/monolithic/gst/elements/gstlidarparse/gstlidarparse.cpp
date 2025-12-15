#include "gstlidarparse.h"
#include <string.h>
#include <vector>
#include <fstream>

GST_DEBUG_CATEGORY_STATIC(gst_lidar_parse_debug);
#define GST_CAT_DEFAULT gst_lidar_parse_debug

enum {
    PROP_0,
    PROP_LOCATION,
    PROP_STRIDE,
    PROP_FRAME_RATE
};

static GstStaticPadTemplate sink_template = GST_STATIC_PAD_TEMPLATE(
    "sink",
    GST_PAD_SINK,
    GST_PAD_ALWAYS,
    GST_STATIC_CAPS_ANY
);

static GstStaticPadTemplate src_template = GST_STATIC_PAD_TEMPLATE(
    "src",
    GST_PAD_SRC,
    GST_PAD_ALWAYS,
    GST_STATIC_CAPS("application/x-raw, "
                    "format=(string)F32_LE, "
                    "channels=(int)1")
);

static void gst_lidar_parse_set_property(GObject *object, guint prop_id,
                                         const GValue *value, GParamSpec *pspec);
static void gst_lidar_parse_get_property(GObject *object, guint prop_id,
                                         GValue *value, GParamSpec *pspec);
static void gst_lidar_parse_finalize(GObject *object);

static gboolean gst_lidar_parse_start(GstBaseTransform *trans);
static gboolean gst_lidar_parse_stop(GstBaseTransform *trans);
static GstFlowReturn gst_lidar_parse_transform_ip(GstBaseTransform *trans, GstBuffer *buffer);
static GstCaps *gst_lidar_parse_transform_caps(GstBaseTransform *trans,
                                                GstPadDirection direction,
                                                GstCaps *caps,
                                                GstCaps *filter);

static void gst_lidar_parse_class_init(GstLidarParseClass *klass);
static void gst_lidar_parse_init(GstLidarParse *filter);

G_DEFINE_TYPE(GstLidarParse, gst_lidar_parse, GST_TYPE_BASE_TRANSFORM);

static void gst_lidar_parse_class_init(GstLidarParseClass *klass) {
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    GstElementClass *gstelement_class = GST_ELEMENT_CLASS(klass);
    GstBaseTransformClass *base_transform_class = GST_BASE_TRANSFORM_CLASS(klass);

    gobject_class->set_property = gst_lidar_parse_set_property;
    gobject_class->get_property = gst_lidar_parse_get_property;
    gobject_class->finalize = gst_lidar_parse_finalize;

    g_object_class_install_property(gobject_class, PROP_LOCATION,
        g_param_spec_string("location", "Location",
                           "Location of the binary file to parse",
                           NULL,
                           (GParamFlags)(G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS)));

    g_object_class_install_property(gobject_class, PROP_STRIDE,
        g_param_spec_int("stride", "Stride",
                        "Stride for processing",
                        1, G_MAXINT, 1,
                        (GParamFlags)(G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS)));

    g_object_class_install_property(gobject_class, PROP_FRAME_RATE,
        g_param_spec_float("frame-rate", "Frame Rate",
                          "Frame rate for output",
                          0.0, G_MAXFLOAT, 0.0,
                          (GParamFlags)(G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS)));

    gst_element_class_set_static_metadata(gstelement_class,
        "Lidar Binary Parser",
        "Filter/Converter",
        "Parses binary lidar data to vector float format",
        "Your Name <your.email@example.com>");

    gst_element_class_add_static_pad_template(gstelement_class, &sink_template);
    gst_element_class_add_static_pad_template(gstelement_class, &src_template);

    base_transform_class->start = GST_DEBUG_FUNCPTR(gst_lidar_parse_start);
    base_transform_class->stop = GST_DEBUG_FUNCPTR(gst_lidar_parse_stop);
    base_transform_class->transform_ip = GST_DEBUG_FUNCPTR(gst_lidar_parse_transform_ip);
    base_transform_class->transform_caps = GST_DEBUG_FUNCPTR(gst_lidar_parse_transform_caps);
    base_transform_class->passthrough_on_same_caps = TRUE;
}

static void gst_lidar_parse_init(GstLidarParse *filter) {
    filter->location = NULL;
    filter->stride = 1;
    filter->frame_rate = 0.0;
    g_mutex_init(&filter->mutex);

    filter->data_size = 0;
    filter->current_index = 0;
    filter->lidar_data.clear();
}

static void gst_lidar_parse_finalize(GObject *object) {
    GstLidarParse *filter = GST_LIDAR_PARSE(object);

    g_free(filter->location);
    g_mutex_clear(&filter->mutex);

    filter->lidar_data.clear();
    filter->data_size = 0;
    filter->current_index = 0;

    G_OBJECT_CLASS(gst_lidar_parse_parent_class)->finalize(object);
}

static void gst_lidar_parse_set_property(GObject *object, guint prop_id,
                                         const GValue *value, GParamSpec *pspec) {
    GstLidarParse *filter = GST_LIDAR_PARSE(object);

    switch (prop_id) {
        case PROP_LOCATION:
            g_free(filter->location);
            filter->location = g_value_dup_string(value);
            break;
        case PROP_STRIDE:
            filter->stride = g_value_get_int(value);
            break;
        case PROP_FRAME_RATE:
            filter->frame_rate = g_value_get_float(value);
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID(object, prop_id, pspec);
            break;
    }
}

static void gst_lidar_parse_get_property(GObject *object, guint prop_id,
                                         GValue *value, GParamSpec *pspec) {
    GstLidarParse *filter = GST_LIDAR_PARSE(object);

    switch (prop_id) {
        case PROP_LOCATION:
            g_value_set_string(value, filter->location);
            break;
        case PROP_STRIDE:
            g_value_set_int(value, filter->stride);
            break;
        case PROP_FRAME_RATE:
            g_value_set_float(value, filter->frame_rate);
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID(object, prop_id, pspec);
            break;
    }
}

static gboolean gst_lidar_parse_start(GstBaseTransform *trans) {
    GstLidarParse *filter = GST_LIDAR_PARSE(trans);

    GST_DEBUG_OBJECT(filter, "Starting lidar parser");
    GST_INFO_OBJECT(filter, "[START] lidarparse, location: %s", filter->location ? filter->location : "(null)");

    if (!filter->current_index) { 
        GstPad *sink_pad = GST_BASE_TRANSFORM_SINK_PAD(trans);
        GstPad *peer_pad = gst_pad_get_peer(sink_pad);
        if (peer_pad) {
            GstElement *upstream_element = gst_pad_get_parent_element(peer_pad);
            if (upstream_element && GST_IS_ELEMENT(upstream_element)) {
                gchar *element_name = gst_element_get_name(upstream_element);
                GST_INFO_OBJECT(filter, "Upstream element name: %s", element_name);
                g_free(element_name);

                if (g_object_class_find_property(G_OBJECT_GET_CLASS(upstream_element), "start-index")) {
                    gint upstream_index = 0;
                    g_object_get(upstream_element, "start-index", &upstream_index, NULL);
                    GST_INFO_OBJECT(filter, "Retrieved upstream index: %d", upstream_index);
                    filter->current_index = upstream_index; // Set initial current_index
                } else {
                    GST_WARNING_OBJECT(filter, "Upstream element does not have an 'index' property");
                }

                g_object_unref(upstream_element);
            }
            gst_object_unref(peer_pad);
        }
    }
    if (!filter->location) {
        GstPad *sink_pad = GST_BASE_TRANSFORM_SINK_PAD(trans);
        GstPad *peer_pad = gst_pad_get_peer(sink_pad);

        if (peer_pad) {
            GstElement *upstream_element = gst_pad_get_parent_element(peer_pad);
            if (upstream_element) {
                gchar *upstream_location = NULL;
                g_object_get(upstream_element, "location", &upstream_location, NULL);

                if (upstream_location) {
                    filter->location = g_strdup(upstream_location);
                    GST_INFO_OBJECT(filter, "Inherited location from upstream: %s", filter->location);
                    g_free(upstream_location);
                } else {
                    GST_ERROR_OBJECT(filter, "Upstream element does not have a 'location' property");
                    GST_WARNING_OBJECT(filter, "Upstream element has no location property");
                }

                g_object_unref(upstream_element);
            }
            gst_object_unref(peer_pad);
        }
    }

    if (!filter->location) {
        GST_ERROR_OBJECT(filter, "No location specified");
        GST_INFO_OBJECT(filter, "[START] Failed: No location");
        return FALSE;
    }

    GST_DEBUG_OBJECT(filter, "Location: %s", filter->location);

    GST_INFO_OBJECT(filter, "[START] lidarparse initialized, no file opening required.");

    GstPad *sink_pad = GST_BASE_TRANSFORM_SINK_PAD(trans);
    GstPad *peer_pad = gst_pad_get_peer(sink_pad);
    GstElement *upstream = NULL;

    if (peer_pad) {
        upstream = gst_pad_get_parent_element(peer_pad);
        gst_object_unref(peer_pad);
    }

    if (!upstream) {
        GST_ERROR_OBJECT(filter, "Failed to retrieve upstream element.");
        return FALSE;
    }

    gint start_index = 0;
    g_object_get(G_OBJECT(upstream), "start-index", &start_index, NULL);

    if (start_index < 0) {
        GST_ERROR_OBJECT(filter, "Invalid start-index (%d)", start_index);
        return FALSE;
    }

    filter->data_size = start_index + 1;
    GST_DEBUG_OBJECT(filter, "Calculated data_size based on start-index (%d): %zu", start_index, filter->data_size);

    return TRUE;
}

static gboolean gst_lidar_parse_stop(GstBaseTransform *trans) {
    GstLidarParse *filter = GST_LIDAR_PARSE(trans);

    GST_DEBUG_OBJECT(filter, "Stopping lidar parser");
    GST_INFO_OBJECT(filter, "[STOP] lidarparse, clearing data, previous size: %lu", (unsigned long)filter->lidar_data.size());

    filter->lidar_data.clear();
    filter->data_size = 0;
    filter->current_index = 0;
    filter->frame_count = 0;

    GST_INFO_OBJECT(filter, "[STOP] Data cleared");

    return TRUE;
}

static GstCaps *gst_lidar_parse_transform_caps(GstBaseTransform *trans,
                                                GstPadDirection direction,
                                                GstCaps *caps,
                                                GstCaps *filter) {
    if (direction == GST_PAD_SINK) {
        return gst_caps_ref(caps);
    } else {
        GstCaps *result = gst_caps_new_simple("application/x-raw",
                                              "format", G_TYPE_STRING, "F32_LE",
                                              "channels", G_TYPE_INT, 1,
                                              "layout", G_TYPE_STRING, "interleaved",
                                              NULL);
        return result;
    }
}

static GstFlowReturn gst_lidar_parse_transform_ip(GstBaseTransform *trans, GstBuffer *buffer) {
    GstLidarParse *filter = GST_LIDAR_PARSE(trans);

    GstMapInfo map;
    gst_buffer_map(buffer, &map, GST_MAP_READ);

    // Frame rate control variables
    static GstClockTime last_frame_time = GST_CLOCK_TIME_NONE;
    GstClockTime current_time = gst_clock_get_time(gst_system_clock_obtain());

    // Calculate frame interval based on frame_rate
    GstClockTime frame_interval = (GstClockTime)(GST_SECOND / filter->frame_rate);

    // Debug information for rate control
    GST_DEBUG_OBJECT(filter, "Current time: %" GST_TIME_FORMAT, GST_TIME_ARGS(current_time));
    GST_DEBUG_OBJECT(filter, "Last frame time: %" GST_TIME_FORMAT, GST_TIME_ARGS(last_frame_time));
    GST_DEBUG_OBJECT(filter, "Frame interval: %" GST_TIME_FORMAT, GST_TIME_ARGS(frame_interval));

    // If this is not the first frame, ensure the frame interval is respected
    if (last_frame_time != GST_CLOCK_TIME_NONE) {
        GstClockTime elapsed_time = current_time - last_frame_time;
        GST_DEBUG_OBJECT(filter, "Elapsed time since last frame: %" GST_TIME_FORMAT, GST_TIME_ARGS(elapsed_time));
        if (elapsed_time < frame_interval) {
            GstClockTime sleep_time = frame_interval - elapsed_time;
            GST_DEBUG_OBJECT(filter, "Sleeping for %" GST_TIME_FORMAT, GST_TIME_ARGS(sleep_time));
            g_usleep(sleep_time / 1000); // Convert nanoseconds to microseconds
        }
    }

    // Update last frame time
    last_frame_time = gst_clock_get_time(gst_system_clock_obtain());

    // Process GstBuffer data directly
    gst_buffer_map(buffer, &map, GST_MAP_READ);

    // Ensure the buffer size is a multiple of sizeof(float)
    if (map.size % sizeof(float) != 0) {
        GST_ERROR_OBJECT(filter, "Buffer size (%lu) is not a multiple of float size (%lu)",
                         map.size, sizeof(float));
        gst_buffer_unmap(buffer, &map);
        return GST_FLOW_ERROR;
    }

    // Parse data as float
    size_t num_floats = map.size / sizeof(float);
    const float *data = reinterpret_cast<const float *>(map.data);

    filter->lidar_data.assign(data, data + num_floats);
    gst_buffer_unmap(buffer, &map);

    // Log the file being read before processing
    static gchar *current_file_name = NULL;

    // Ensure proper memory management for current_file_name
    if (current_file_name) {
        g_free(current_file_name);
        current_file_name = NULL; 
    }

    // Construct the file name using the current index
    current_file_name = g_strdup_printf(filter->location, filter->current_index);

    // Check if the file exists
    if (access(current_file_name, F_OK) != 0) {
        GST_INFO_OBJECT(filter, "File not found: %s", current_file_name);
        g_free(current_file_name);
        current_file_name = NULL; 
        return GST_FLOW_EOS; 
    }

    GST_INFO_OBJECT(filter, "Processing file: %s", current_file_name);

    // Log the first few parsed float values for debugging
    size_t log_count = std::min(num_floats, static_cast<size_t>(10));
    GST_INFO_OBJECT(filter, "Parsed %lu float samples. First %lu values: ", num_floats, log_count);
    for (size_t i = 0; i < log_count; ++i) {
        GST_INFO_OBJECT(filter, "Value[%lu]: %f", i, filter->lidar_data[i]);
    }

    // Free current_file_name after processing
    if (current_file_name) {
        g_free(current_file_name);
        current_file_name = NULL; 
    }

    // Allocate a new GstBuffer
    GstBuffer *out_buffer = gst_buffer_new_allocate(NULL, filter->lidar_data.size() * sizeof(float), NULL);
    if (!out_buffer) {
        GST_ERROR_OBJECT(filter, "Failed to allocate GstBuffer");
        return GST_FLOW_ERROR;
    }

    // Map the buffer for writing
    GstMapInfo out_map;
    gst_buffer_map(out_buffer, &out_map, GST_MAP_WRITE);
    memcpy(out_map.data, filter->lidar_data.data(), filter->lidar_data.size() * sizeof(float));
    gst_buffer_unmap(out_buffer, &out_map);

    // Push the new buffer to the downstream element
    GstFlowReturn ret = gst_pad_push(GST_BASE_TRANSFORM_SRC_PAD(trans), out_buffer);
    if (ret != GST_FLOW_OK) {
        GST_ERROR_OBJECT(filter, "Failed to push buffer to downstream: %s", gst_flow_get_name(ret));
        gst_buffer_unref(out_buffer); // Unref the buffer in case of failure
        return ret;
    }

    filter->current_index += filter->stride;
    GST_DEBUG_OBJECT(filter, "Updated current_index: %zu, stride: %d", filter->current_index, filter->stride);

    return GST_FLOW_OK;
}

static gboolean plugin_init(GstPlugin *plugin) {
    GST_DEBUG_CATEGORY_INIT(gst_lidar_parse_debug, "lidarparse", 0, "Lidar Binary Parser");

    return gst_element_register(plugin, "lidarparse", GST_RANK_NONE, GST_TYPE_LIDAR_PARSE);
}

#ifndef PACKAGE
#define PACKAGE "lidarparse"
#endif

GST_PLUGIN_DEFINE(
    GST_VERSION_MAJOR,
    GST_VERSION_MINOR,
    lidarparse,
    "Lidar Binary Parser",
    plugin_init,
    "1.0",
    "LGPL",
    "dlstreamer",
    "https://github.com/dlstreamer/dlstreamer"
)
