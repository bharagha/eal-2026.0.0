#ifndef __GST_RADAR_PARSE_H__
#define __GST_RADAR_PARSE_H__

#include <gst/gst.h>
#include <gst/base/gstbasetransform.h>
#include <complex>
#include <vector>
#include <fstream>

G_BEGIN_DECLS

#define GST_TYPE_RADAR_PARSE (gst_radar_parse_get_type())
#define GST_RADAR_PARSE(obj) (G_TYPE_CHECK_INSTANCE_CAST((obj), GST_TYPE_RADAR_PARSE, GstRadarParse))
#define GST_RADAR_PARSE_CLASS(klass) (G_TYPE_CHECK_CLASS_CAST((klass), GST_TYPE_RADAR_PARSE, GstRadarParseClass))
#define GST_IS_RADAR_PARSE(obj) (G_TYPE_CHECK_INSTANCE_TYPE((obj), GST_TYPE_RADAR_PARSE))
#define GST_IS_RADAR_PARSE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), GST_TYPE_RADAR_PARSE))

typedef struct _GstRadarParse GstRadarParse;
typedef struct _GstRadarParseClass GstRadarParseClass;

struct _GstRadarParse {
    GstBaseTransform base_transform;
    
    // Properties
    gchar *location;
    gint stride;
    gfloat frame_rate;
    
    // Internal state
    std::vector<std::complex<float>> radar_data;
    gsize data_size;
    gint64 frame_count;
    GMutex mutex;
};

struct _GstRadarParseClass {
    GstBaseTransformClass parent_class;
};

GType gst_radar_parse_get_type(void);

G_END_DECLS

#endif /* __GST_RADAR_PARSE_H__ */
