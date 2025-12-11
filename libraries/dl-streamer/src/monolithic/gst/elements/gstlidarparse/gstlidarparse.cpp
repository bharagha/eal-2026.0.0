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

    std::ifstream file(filter->location, std::ios::binary | std::ios::ate);
    if (!file) {
        GST_ERROR_OBJECT(filter, "Failed to open file: %s", filter->location);
        GST_INFO_OBJECT(filter, "[START] Failed: Cannot open file");
        return FALSE;
    }

    std::streamsize size = file.tellg();
    file.seekg(0, std::ios::beg);
    GST_INFO_OBJECT(filter, "File size: %ld bytes", (long)size);

    gsize samples_to_read = size / sizeof(float);
    GST_INFO_OBJECT(filter, "Samples to read: %lu", (unsigned long)samples_to_read);

    filter->lidar_data.resize(samples_to_read);
    file.read(reinterpret_cast<char*>(filter->lidar_data.data()), size);
    filter->data_size = filter->lidar_data.size();
    GST_INFO_OBJECT(filter, "Read data_size: %lu", (unsigned long)filter->data_size);

    file.close();

    GST_INFO_OBJECT(filter, "Loaded %lu float samples from %s",
                   filter->data_size, filter->location);

    filter->current_index = 0;

    GstEvent *stream_start_event = gst_event_new_stream_start("lidarparse-stream");
    if (!gst_pad_push_event(GST_BASE_TRANSFORM_SRC_PAD(trans), stream_start_event)) {
        GST_ERROR_OBJECT(filter, "Failed to push stream-start event");
        GST_INFO_OBJECT(filter, "[START] Failed: stream-start event");
        return FALSE;
    }
    GST_DEBUG_OBJECT(filter, "Stream-start event pushed");

    GstCaps *caps = gst_caps_new_simple("application/x-raw",
                                        "format", G_TYPE_STRING, "F32_LE",
                                        "channels", G_TYPE_INT, 1,
                                        NULL);

    if (!gst_pad_set_caps(GST_BASE_TRANSFORM_SRC_PAD(trans), caps)) {
        GST_ERROR_OBJECT(filter, "Failed to set caps on src pad");
        GST_INFO_OBJECT(filter, "[START] Failed: set caps");
        gst_caps_unref(caps);
        return FALSE;
    }

    GST_DEBUG_OBJECT(filter, "Caps set on src pad: %s", gst_caps_to_string(caps));
    GST_INFO_OBJECT(filter, "[START] Success");
    gst_caps_unref(caps);

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
    gst_buffer_map(buffer, &map, GST_MAP_WRITE);

    GST_DEBUG_OBJECT(filter, "[TRANSFORM_IP] buffer size: %lu", (unsigned long)map.size);
    GST_INFO_OBJECT(filter, "[TRANSFORM_IP] lidar_data size: %lu", (unsigned long)filter->data_size);

    size_t stride = filter->stride > 0 ? filter->stride : 1;
    size_t current = filter->current_index;
    size_t remain = (current < filter->data_size) ? (filter->data_size - current) : 0;
    size_t to_copy = (remain >= stride) ? stride : remain;

    if (to_copy > 0) {
        memcpy(map.data, &filter->lidar_data[current], to_copy * sizeof(float));
        if (to_copy < stride) {
            memset((char*)map.data + to_copy * sizeof(float), 0, (stride - to_copy) * sizeof(float));
        }
        filter->current_index += to_copy;
    } else {
        memset(map.data, 0, stride * sizeof(float));
    }

    for (size_t i = 0; i < to_copy && i < 5; ++i) {
        GST_DEBUG_OBJECT(filter, "[TRANSFORM_IP] sample[%zu]=%f", current + i, filter->lidar_data[current + i]);
    }
    GST_INFO_OBJECT(filter, "[TRANSFORM_IP] output_data size: %lu", (unsigned long)to_copy);

    gst_buffer_unmap(buffer, &map);

    GST_DEBUG_OBJECT(filter, "[TRANSFORM_IP] buffer unmapped, returning GST_FLOW_OK");

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
