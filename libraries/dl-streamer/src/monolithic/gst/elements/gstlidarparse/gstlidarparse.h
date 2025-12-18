#ifndef __GST_LIDAR_PARSE_H__
#define __GST_LIDAR_PARSE_H__

#include <gst/gst.h>
#include <gst/base/gstbasetransform.h>
#include <vector>

G_BEGIN_DECLS

#define GST_TYPE_LIDAR_PARSE (gst_lidar_parse_get_type())
#define GST_LIDAR_PARSE(obj) (G_TYPE_CHECK_INSTANCE_CAST((obj), GST_TYPE_LIDAR_PARSE, GstLidarParse))
#define GST_LIDAR_PARSE_CLASS(klass) (G_TYPE_CHECK_CLASS_CAST((klass), GST_TYPE_LIDAR_PARSE, GstLidarParseClass))
#define GST_IS_LIDAR_PARSE(obj) (G_TYPE_CHECK_INSTANCE_TYPE((obj), GST_TYPE_LIDAR_PARSE))
#define GST_IS_LIDAR_PARSE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), GST_TYPE_LIDAR_PARSE))

typedef struct _GstLidarParse GstLidarParse;
typedef struct _GstLidarParseClass GstLidarParseClass;

struct _GstLidarParse {
    GstBaseTransform parent;

    gchar *location;
    gint stride;
    gfloat frame_rate;
    GMutex mutex;

    std::vector<float> lidar_data;
    size_t data_size;
    size_t current_index;
    guint64 file_counter;  // Instance variable for stride counting
    guint total_files; // Total number of files to process
};

struct _GstLidarParseClass {
    GstBaseTransformClass parent_class;
};

GType gst_lidar_parse_get_type(void);

G_END_DECLS

#endif /* __GST_LIDAR_PARSE_H__ */
