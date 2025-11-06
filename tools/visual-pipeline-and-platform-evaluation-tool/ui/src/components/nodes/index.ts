import FileSrcNode, { FileSrcNodeWidth } from "./FileSrcNode";
import QtdemuxNode from "./QtdemuxNode";
import H264ParseNode from "./H264ParseNode";
import VAH264DecNode from "./VAH264DecNode";
import GVAFpsCounterNode from "./GVAFpsCounterNode";
import GVADetectNode, { GVADetectNodeWidth } from "./GVADetectNode";
import Queue2Node from "./Queue2Node";
import GVATrackNode from "./GVATrackNode";
import GVAWatermarkNode from "./GVAWatermarkNode";
import GVAMetaConvertNode, {
  GVAMetaConvertNodeWidth,
} from "./GVAMetaConvertNode";
import GVAMetaPublishNode, {
  GVAMetaPublishNodeWidth,
} from "./GVAMetaPublishNode";
import FakeSinkNode from "./FakeSinkNode";
import VideoXRawNode from "./VideoXRawNode";
import VAPostProcNode from "./VAPostProcNode";
import VideoXRawWithDimensionsNode from "./VideoXRawWithDimensionsNode";
import Mp4MuxNode from "./Mp4MuxNode";
import FileSinkNode from "./FileSinkNode";
import VAH264EncNode from "./VAH264EncNode";
import Decodebin3Node from "./Decodebin3Node";
import QueueNode, { QueueNodeWidth } from "./QueueNode";
import GVAClassifyNode from "./GVAClassifyNode";

export const nodeTypes = {
  filesrc: FileSrcNode,
  qtdemux: QtdemuxNode,
  h264parse: H264ParseNode,
  vah264dec: VAH264DecNode,
  gvafpscounter: GVAFpsCounterNode,
  gvadetect: GVADetectNode,
  queue2: Queue2Node,
  gvatrack: GVATrackNode,
  gvawatermark: GVAWatermarkNode,
  gvametaconvert: GVAMetaConvertNode,
  gvametapublish: GVAMetaPublishNode,
  fakesink: FakeSinkNode,
  "video/x-raw(memory:VAMemory)": VideoXRawNode,
  vapostproc: VAPostProcNode,
  "video/x-raw": VideoXRawWithDimensionsNode,
  mp4mux: Mp4MuxNode,
  filesink: FileSinkNode,
  vah264enc: VAH264EncNode,
  decodebin3: Decodebin3Node,
  queue: QueueNode,
  gvaclassify: GVAClassifyNode,
};

// Node widths mapping - read from individual components
export const nodeWidths: Record<string, number> = {
  filesrc: FileSrcNodeWidth,
  gvadetect: GVADetectNodeWidth,
  gvametaconvert: GVAMetaConvertNodeWidth,
  gvametapublish: GVAMetaPublishNodeWidth,
  queue: QueueNodeWidth,
};

// Default node width for components that don't specify their own
export const defaultNodeWidth = 220;

export default nodeTypes;
