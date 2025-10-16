/*******************************************************************************
 * Copyright (C) 2018-2025 Intel Corporation
 *
 * SPDX-License-Identifier: MIT
 ******************************************************************************/

#pragma once

#include "gstgvaclassify.h"

#include <gst/analytics/analytics.h>
#include <gst/base/gstbasetransform.h>
#include <gst/gst.h>
#include <gst/video/video.h>

G_BEGIN_DECLS

struct ClassificationHistory;
struct ClassificationHistory *create_classification_history(GstGvaClassify *gva_classify);
void release_classification_history(struct ClassificationHistory *classification_history);
void fill_roi_params_from_history(struct ClassificationHistory *classification_history, GstBuffer *buffer);

G_END_DECLS

#ifdef __cplusplus
#include "gst_smart_pointer_types.hpp"
#include "lru_cache.h"

#include <memory>
#include <mutex>
#include <vector>
#include <condition_variable>

const size_t CLASSIFICATION_HISTORY_SIZE = 100;

struct ClassificationHistory {
  public:
    struct ROIClassificationHistory {
      uint64_t frame_of_last_update;
      bool updated;
      std::vector<GstStructureSharedPtr> last_tensors;

      ROIClassificationHistory(uint64_t frame_of_last_update = {},
                   std::vector<GstStructureSharedPtr> last_tensors = {})
        : frame_of_last_update(frame_of_last_update), updated(false), last_tensors(last_tensors) {
      }
    };

    ClassificationHistory(GstGvaClassify *gva_classify);

    bool IsROIClassificationNeeded(GstVideoRegionOfInterestMeta *roi, GstBuffer *buffer, uint64_t current_num_frame);
    void UpdateROIParams(int roi_id, const std::vector<GstStructure *> &roi_param);
    void FillROIParams(GstBuffer *buffer);
    LRUCache<int, ROIClassificationHistory> &GetHistory();

  private:
    void CheckExistingAndReaddObjectId(int roi_id);

    GstGvaClassify *gva_classify;
    LRUCache<int, ROIClassificationHistory> history;
    std::condition_variable cv;
    std::mutex history_mutex;
};
#endif
