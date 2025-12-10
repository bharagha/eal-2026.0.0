#include "gstradarparse.h"
#include <gst/video/video.h>
#include <gst/audio/audio.h>
#include <string.h>

GST_DEBUG_CATEGORY_STATIC(gst_radar_parse_debug);
#define GST_CAT_DEFAULT gst_radar_parse_debug

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
    GST_STATIC_CAPS("application/x-complex-float; "
                    "application/x-raw, "
                    "format=(string)F32_LE, "
                    "channels=(int)2")
);

static void gst_radar_parse_set_property(GObject *object, guint prop_id,
                                         const GValue *value, GParamSpec *pspec);
static void gst_radar_parse_get_property(GObject *object, guint prop_id,
                                         GValue *value, GParamSpec *pspec);
static void gst_radar_parse_finalize(GObject *object);

static gboolean gst_radar_parse_start(GstBaseTransform *trans);
static gboolean gst_radar_parse_stop(GstBaseTransform *trans);
static GstFlowReturn gst_radar_parse_transform_ip(GstBaseTransform *trans, GstBuffer *buffer);
static GstCaps *gst_radar_parse_transform_caps(GstBaseTransform *trans,
                                                GstPadDirection direction,
                                                GstCaps *caps,
                                                GstCaps *filter);

static void gst_radar_parse_class_init(GstRadarParseClass *klass);
static void gst_radar_parse_init(GstRadarParse *filter);

G_DEFINE_TYPE(GstRadarParse, gst_radar_parse, GST_TYPE_BASE_TRANSFORM);

static void gst_radar_parse_class_init(GstRadarParseClass *klass) {
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    GstElementClass *gstelement_class = GST_ELEMENT_CLASS(klass);
    GstBaseTransformClass *base_transform_class = GST_BASE_TRANSFORM_CLASS(klass);

    gobject_class->set_property = gst_radar_parse_set_property;
    gobject_class->get_property = gst_radar_parse_get_property;
    gobject_class->finalize = gst_radar_parse_finalize;

    // Install properties
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

    // Set element metadata
    gst_element_class_set_static_metadata(gstelement_class,
        "Radar Binary Parser",
        "Filter/Converter",
        "Parses binary radar data to complex float format",
        "Your Name <your.email@example.com>");

    // Add pads
    gst_element_class_add_static_pad_template(gstelement_class, &sink_template);
    gst_element_class_add_static_pad_template(gstelement_class, &src_template);

    // Set virtual functions
    base_transform_class->start = GST_DEBUG_FUNCPTR(gst_radar_parse_start);
    base_transform_class->stop = GST_DEBUG_FUNCPTR(gst_radar_parse_stop);
    base_transform_class->transform_ip = GST_DEBUG_FUNCPTR(gst_radar_parse_transform_ip);
    base_transform_class->transform_caps = GST_DEBUG_FUNCPTR(gst_radar_parse_transform_caps);
    base_transform_class->passthrough_on_same_caps = TRUE;
}

static void gst_radar_parse_init(GstRadarParse *filter) {
    filter->location = NULL;
    filter->stride = 1;
    filter->frame_rate = 0.0;
    filter->data_size = 0;
    filter->frame_count = 0;
    g_mutex_init(&filter->mutex);
}

static void gst_radar_parse_finalize(GObject *object) {
    GstRadarParse *filter = GST_RADAR_PARSE(object);
    
    g_free(filter->location);
    g_mutex_clear(&filter->mutex);
    
    G_OBJECT_CLASS(gst_radar_parse_parent_class)->finalize(object);
}

static void gst_radar_parse_set_property(GObject *object, guint prop_id,
                                         const GValue *value, GParamSpec *pspec) {
    GstRadarParse *filter = GST_RADAR_PARSE(object);
    
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

static void gst_radar_parse_get_property(GObject *object, guint prop_id,
                                         GValue *value, GParamSpec *pspec) {
    GstRadarParse *filter = GST_RADAR_PARSE(object);
    
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

static gboolean gst_radar_parse_start(GstBaseTransform *trans) {
    GstRadarParse *filter = GST_RADAR_PARSE(trans);

    GST_DEBUG_OBJECT(filter, "Starting radar parser");

    // If location is not set, try to get it from upstream
    if (!filter->location) {
        GstPad *sink_pad = GST_BASE_TRANSFORM_SINK_PAD(trans);  // Use macro to get sink pad
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
                }

                g_object_unref(upstream_element);
            }
            gst_object_unref(peer_pad);
        }
    }

    if (!filter->location) {
        GST_ERROR_OBJECT(filter, "No location specified");
        return FALSE;
    }

    GST_DEBUG_OBJECT(filter, "Location: %s", filter->location);

    // Read binary file
    std::ifstream file(filter->location, std::ios::binary | std::ios::ate);
    if (!file) {
        GST_ERROR_OBJECT(filter, "Failed to open file: %s", filter->location);
        return FALSE;
    }

    std::streamsize size = file.tellg();
    file.seekg(0, std::ios::beg);

    // Calculate number of complex samples
    gsize samples_to_read = size / sizeof(std::complex<float>);
    filter->radar_data.resize(samples_to_read);

    // Read complex data
    file.read(reinterpret_cast<char*>(filter->radar_data.data()), size);
    filter->data_size = filter->radar_data.size();

    file.close();

    GST_INFO_OBJECT(filter, "Loaded %lu complex samples from %s", 
                   filter->data_size, filter->location);

    // Send stream-start event
    GstEvent *stream_start_event = gst_event_new_stream_start("radarparse-stream");
    if (!gst_pad_push_event(GST_BASE_TRANSFORM_SRC_PAD(trans), stream_start_event)) {
        GST_ERROR_OBJECT(filter, "Failed to push stream-start event");
        return FALSE;
    }
    GST_DEBUG_OBJECT(filter, "Stream-start event pushed");

    // Ensure caps are correctly set on the src pad
    // Caps describe the format of the data flowing through the pad
    GstCaps *caps = gst_caps_new_simple("application/x-complex-float",  // Define the media type
                                        "format", G_TYPE_STRING, "F32_LE",  // Specify the data format
                                        "channels", G_TYPE_INT, 2,  // Number of channels (real and imaginary)
                                        NULL);

    // Set the caps on the src pad to ensure downstream elements interpret the data correctly
    if (!gst_pad_set_caps(GST_BASE_TRANSFORM_SRC_PAD(trans), caps)) {
        GST_ERROR_OBJECT(filter, "Failed to set caps on src pad");
        gst_caps_unref(caps);
        return FALSE;
    }

    GST_DEBUG_OBJECT(filter, "Caps set on src pad: %s", gst_caps_to_string(caps));
    gst_caps_unref(caps);

    return TRUE;
}

static gboolean gst_radar_parse_stop(GstBaseTransform *trans) {
    GstRadarParse *filter = GST_RADAR_PARSE(trans);
    
    GST_DEBUG_OBJECT(filter, "Stopping radar parser");
    
    // Clear data
    filter->radar_data.clear();
    filter->data_size = 0;
    filter->frame_count = 0;
    
    return TRUE;
}

static GstCaps *gst_radar_parse_transform_caps(GstBaseTransform *trans,
                                                GstPadDirection direction,
                                                GstCaps *caps,
                                                GstCaps *filter) {
    if (direction == GST_PAD_SINK) {
        // We accept any caps on sink
        return gst_caps_ref(caps);
    } else {
        // On source, we output complex float data
        GstCaps *result = gst_caps_new_simple("application/x-complex-float",
                                              "format", G_TYPE_STRING, "F32_LE",
                                              "channels", G_TYPE_INT, 2,
                                              NULL);
        return result;
    }
}

static GstFlowReturn gst_radar_parse_transform_ip(GstBaseTransform *trans, GstBuffer *buffer) {
    GstRadarParse *filter = GST_RADAR_PARSE(trans);

    g_mutex_lock(&filter->mutex);

    // Check if we have data
    if (filter->radar_data.empty()) {
        g_mutex_unlock(&filter->mutex);
        GST_ERROR_OBJECT(filter, "No radar data loaded");
        return GST_FLOW_ERROR;
    }

    // Calculate how many samples to output based on stride
    gsize output_size = filter->data_size / filter->stride;
    if (output_size == 0) {
        output_size = 1;
    }

    // Create output buffer
    GstBuffer *outbuf = gst_buffer_new_allocate(NULL, 
                                               output_size * sizeof(std::complex<float>), 
                                               NULL);

    GstMapInfo map;
    if (!gst_buffer_map(outbuf, &map, GST_MAP_WRITE)) {
        g_mutex_unlock(&filter->mutex);
        gst_buffer_unref(outbuf);
        return GST_FLOW_ERROR;
    }

    // Copy data with stride and convert to complex float
    std::complex<float> *output = reinterpret_cast<std::complex<float>*>(map.data);
    for (gsize i = 0; i < output_size; i++) {
        output[i] = filter->radar_data[i * filter->stride];
        GST_DEBUG_OBJECT(filter, "Complex number: real=%f, imag=%f",
                         std::real(output[i]), std::imag(output[i]));
    }

    gst_buffer_unmap(outbuf, &map);

    // Set caps on buffer
    GstCaps *caps = gst_caps_new_simple("application/x-complex-float",
                                        "format", G_TYPE_STRING, "F32_LE",
                                        "channels", G_TYPE_INT, 2,
                                        NULL);
    gst_pad_set_caps(GST_BASE_TRANSFORM_SRC_PAD(trans), caps);
    gst_caps_unref(caps);

    // Apply frame rate control if specified
    if (filter->frame_rate > 0.0) {
        GstClockTime interval = GST_SECOND / filter->frame_rate;
        gst_base_transform_set_gap_aware(trans, TRUE);

        // Add timestamp
        GstClockTime timestamp = filter->frame_count * interval;
        GST_BUFFER_PTS(outbuf) = timestamp;
        GST_BUFFER_DTS(outbuf) = timestamp;
        GST_BUFFER_DURATION(outbuf) = interval;

        filter->frame_count++;
    }

    g_mutex_unlock(&filter->mutex);

    GST_DEBUG_OBJECT(filter, "Processed buffer with %lu complex samples", output_size);

    // Push the new buffer downstream
    return gst_pad_push(GST_BASE_TRANSFORM_SRC_PAD(trans), outbuf);
}

static gboolean plugin_init(GstPlugin *plugin) {
    GST_DEBUG_CATEGORY_INIT(gst_radar_parse_debug, "radarparse", 0, "Radar Binary Parser");
    
    return gst_element_register(plugin, "radarparse", GST_RANK_NONE, GST_TYPE_RADAR_PARSE);
}

#ifndef PACKAGE
#define PACKAGE "radarparse"
#endif

GST_PLUGIN_DEFINE(
    GST_VERSION_MAJOR,
    GST_VERSION_MINOR,
    radarparse,
    "Radar Binary Parser",
    plugin_init,
    "1.0",
    "LGPL",
    "dlstreamer",
    "https://github.com/dlstreamer/dlstreamer"
)
