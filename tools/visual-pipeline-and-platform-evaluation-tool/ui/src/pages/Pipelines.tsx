import { useParams } from "react-router";
import {
  useGetPipelineQuery,
  useRunPipelineMutation,
  useStopPipelineInstanceMutation,
} from "@/api/api.generated";
import {
  Background,
  BackgroundVariant,
  Controls,
  type Edge,
  type Node,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type NodeMouseHandler,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect, useState } from "react";
import dagre from "dagre";
import { nodeTypes, nodeWidths, defaultNodeWidth } from "@/components/nodes";
import NodeDataPanel from "@/components/NodeDataPanel";
import FpsDisplay from "@/components/FpsDisplay";
import { Save, Play, Square } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { toast } from "sonner";

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeHeight = 120;

// Function to get node width based on node type
const getNodeWidth = (nodeType: string): number => {
  return nodeWidths[nodeType] || defaultNodeWidth;
};

const transformApiNodes = (apiNodes: Node[]): Node[] => {
  return apiNodes.map((node) => {
    // Transform nodes based on their type
    // if (node.type === "filesrc") {
    //   return {
    //     ...node,
    //     type: "filesrc", // This will use our custom FileSrcNode component
    //     data: {
    //       ...node.data,
    //       location: node.data.location || "/path/to/default/file.mp4", // Add location property
    //     },
    //   };
    // }
    //
    // if (node.type === "qtdemux") {
    //   return {
    //     ...node,
    //     type: "qtdemux", // This will use our custom QtdemuxNode component
    //     data: {
    //       ...node.data,
    //     },
    //   };
    // }
    //
    // if (node.type === "h264parse") {
    //   return {
    //     ...node,
    //     type: "h264parse", // This will use our custom H264ParseNode component
    //     data: {
    //       ...node.data,
    //     },
    //   };
    // }
    //
    // if (node.type === "vah264dec") {
    //   return {
    //     ...node,
    //     type: "vah264dec", // This will use our custom VAH264DecNode component
    //     data: {
    //       ...node.data,
    //     },
    //   };
    // }
    //
    // if (node.type === "gvafpscounter") {
    //   return {
    //     ...node,
    //     type: "gvafpscounter", // This will use our custom GVAFpsCounterNode component
    //     data: {
    //       ...node.data,
    //       "starting-frame": node.data["starting-frame"] || "0", // Add starting-frame property
    //     },
    //   };
    // }
    //
    // if (node.type === "gvadetect") {
    //   return {
    //     ...node,
    //     type: "gvadetect", // This will use our custom GVADetectNode component
    //     data: {
    //       ...node.data,
    //       model: node.data.model || "", // Add model property
    //       device: node.data.device || "", // Add device property
    //       "pre-process-backend": node.data["pre-process-backend"] || "", // Add pre-process-backend property
    //       "inference-backend": node.data["inference-backend"] || "", // Add inference-backend property
    //     },
    //   };
    // }
    //
    // if (node.type === "queue2") {
    //   return {
    //     ...node,
    //     type: "queue2", // This will use our custom Queue2Node component
    //     data: {
    //       ...node.data,
    //     },
    //   };
    // }
    //
    // if (node.type === "gvatrack") {
    //   return {
    //     ...node,
    //     type: "gvatrack", // This will use our custom GVATrackNode component
    //     data: {
    //       ...node.data,
    //       "tracking-type": node.data["tracking-type"] || "", // Add tracking-type property
    //     },
    //   };
    // }
    //
    // if (node.type === "gvawatermark") {
    //   return {
    //     ...node,
    //     type: "gvawatermark", // This will use our custom GVAWatermarkNode component
    //     data: {
    //       ...node.data,
    //     },
    //   };
    // }
    //
    // if (node.type === "gvametaconvert") {
    //   return {
    //     ...node,
    //     type: "gvametaconvert", // This will use our custom GVAMetaConvertNode component
    //     data: node.data,
    //   };
    // }
    //
    // if (node.type === "gvametapublish") {
    //   return {
    //     ...node,
    //     type: "gvametapublish", // This will use our custom GVAMetaPublishNode component
    //     data: {
    //       ...node.data,
    //       method: node.data.method || "", // Add method property
    //       "file-path": node.data["file-path"] || "", // Add file-path property
    //     },
    //   };
    // }
    //
    // if (node.type === "fakesink") {
    //   return {
    //     ...node,
    //     type: "fakesink", // This will use our custom FakeSinkNode component
    //     data: {
    //       ...node.data,
    //     },
    //   };
    // }
    //
    // if (node.type === "video/x-raw(memory:VAMemory)") {
    //   return {
    //     ...node,
    //     type: "video/x-raw(memory:VAMemory)", // This will use our custom VideoXRawNode component
    //     data: {
    //       ...node.data,
    //     },
    //   };
    // }
    //
    // if (node.type === "vapostproc") {
    //   return {
    //     ...node,
    //     type: "vapostproc", // This will use our custom VAPostProcNode component
    //     data: {
    //       ...node.data,
    //     },
    //   };
    // }
    //
    // if (node.type === "video/x-raw") {
    //   return {
    //     ...node,
    //     type: "video/x-raw", // This will use our custom VideoXRawWithDimensionsNode component
    //     data: {
    //       ...node.data,
    //       width: node.data.width || "", // Add width property
    //       height: node.data.height || "", // Add height property
    //     },
    //   };
    // }
    //
    // if (node.type === "mp4mux") {
    //   return {
    //     ...node,
    //     type: "mp4mux", // This will use our custom Mp4MuxNode component
    //     data: {
    //       ...node.data,
    //     },
    //   };
    // }
    //
    // if (node.type === "filesink") {
    //   return {
    //     ...node,
    //     type: "filesink", // This will use our custom FileSinkNode component
    //     data: {
    //       ...node.data,
    //       location: node.data.location || "/path/to/output/file.mp4", // Add location property
    //     },
    //   };
    // }
    //
    // if (node.type === "vah264enc") {
    //   return {
    //     ...node,
    //     type: "vah264enc", // This will use our custom VAH264EncNode component
    //     data: {
    //       ...node.data,
    //     },
    //   };
    // }
    //
    // if (node.type === "decodebin3") {
    //   return {
    //     ...node,
    //     type: "decodebin3", // This will use our custom Decodebin3Node component
    //     data: {
    //       ...node.data,
    //     },
    //   };
    // }
    //
    // if (node.type === "queue") {
    //   return {
    //     ...node,
    //     type: "queue", // This will use our custom QueueNode component
    //     data: {
    //       ...node.data,
    //     },
    //   };
    // }
    //
    // if (node.type === "gvaclassify") {
    //   return {
    //     ...node,
    //     type: "gvaclassify", // This will use our custom GVAClassifyNode component
    //     data: {
    //       ...node.data,
    //       model: node.data.model || "", // Add model property
    //     },
    //   };
    // }

    // For other node types, return as default node
    return {
      ...node,
      type: node.type, // React Flow's default node type
    };
  });
};

const getLayoutedElements = (
  nodes: Node[],
  edges: Edge[],
  direction = "LR",
) => {
  const isHorizontal = direction === "LR";
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    const currentNodeWidth = getNodeWidth(node.type || "default");
    dagreGraph.setNode(node.id, {
      width: currentNodeWidth,
      height: nodeHeight,
    });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    const currentNodeWidth = getNodeWidth(node.type || "default");
    return {
      ...node,
      targetPosition: isHorizontal ? Position.Left : Position.Top,
      sourcePosition: isHorizontal ? Position.Right : Position.Bottom,
      position: {
        x: nodeWithPosition.x - currentNodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
};

type UrlParams = {
  id: string;
};

const Pipelines = () => {
  const { id } = useParams<UrlParams>();
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [pipelineInstanceId, setPipelineInstanceId] = useState<string | null>(
    null,
  );

  const { data, isSuccess } = useGetPipelineQuery(
    {
      name: "predefined_pipelines",
      version: id!,
    },
    {
      skip: !id,
    },
  );

  const [runPipeline, { isLoading: isRunning }] = useRunPipelineMutation();
  const [stopPipelineInstance, { isLoading: isStopping }] =
    useStopPipelineInstanceMutation();

  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  // Handle node click to show data panel
  const onNodeClick: NodeMouseHandler = (event, node) => {
    event.stopPropagation();
    setSelectedNode(node);
  };

  // Handle background click to deselect node
  const onPaneClick = () => {
    setSelectedNode(null);
  };

  // Handle node data updates
  const handleNodeDataUpdate = (
    nodeId: string,
    updatedData: Record<string, unknown>,
  ) => {
    setNodes((currentNodes) =>
      currentNodes.map((node) =>
        node.id === nodeId ? { ...node, data: updatedData } : node,
      ),
    );
  };

  // Handle pipeline execution
  const handleRunPipeline = async () => {
    if (!id) return;

    try {
      // Convert ReactFlow nodes to API format
      const apiNodes = nodes.map((node) => ({
        id: node.id,
        type: node.type || "default",
        data: Object.fromEntries(
          Object.entries(node.data || {}).map(([key, value]) => [
            key,
            String(value),
          ]),
        ),
      }));

      const response = await runPipeline({
        name: "predefined_pipelines",
        version: id,
        pipelineRequestRunInput: {
          async_: true,
          source: {
            type: "uri",
            uri: "https://storage.openvinotoolkit.org/repositories/openvino_notebooks/data/data/video/people.mp4",
          },
          parameters: {
            inferencing_channels: 20,
            recording_channels: 0,
            launch_config: {
              nodes: apiNodes,
              edges,
            },
          },
          tags: {
            additionalProp1: "string",
          },
        },
      }).unwrap();

      // Store the instance ID from the response
      if (
        response &&
        typeof response === "object" &&
        "instance_id" in response
      ) {
        setPipelineInstanceId(response.instance_id as string);
      }

      // Handle success (could show a toast notification)
      toast.success("Pipeline run started", {
        description: new Date().toISOString(),
      });
      console.log("Pipeline started successfully");
    } catch (error) {
      // Handle error (could show an error toast)
      toast.error("Failed to start pipeline", {
        description: error instanceof Error ? error.message : "Unknown error",
      });
      console.error("Failed to start pipeline:", error);
    }
  };

  // Handle pipeline stop
  const handleStopPipeline = async () => {
    if (!pipelineInstanceId) return;

    try {
      await stopPipelineInstance({
        instanceId: pipelineInstanceId,
      }).unwrap();

      // Clear the instance ID
      setPipelineInstanceId(null);

      // Handle success
      toast.success("Pipeline stopped", {
        description: new Date().toISOString(),
      });
      console.log("Pipeline stopped successfully");
    } catch (error) {
      // Handle error
      toast.error("Failed to stop pipeline", {
        description: error instanceof Error ? error.message : "Unknown error",
      });
      console.error("Failed to stop pipeline:", error);
    }
  };

  useEffect(() => {
    if (isSuccess && data?.launch_config) {
      // Get the raw nodes and edges from API
      const rawNodes = data.launch_config.nodes || [];
      const rawEdges = data.launch_config.edges || [];

      // Transform nodes to include custom types and properties
      const transformedNodes = transformApiNodes(rawNodes as Node[]);

      // Apply Dagre layout to position nodes automatically
      const { nodes: layoutedNodes, edges: layoutedEdges } =
        getLayoutedElements(
          transformedNodes,
          rawEdges,
          "LR", // Top to Bottom layout, can be changed to "LR" for Left to Right
        );

      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
    }
  }, [isSuccess, data, setNodes, setEdges]);

  if (isSuccess) {
    return (
      <div style={{ width: "100%", height: "100vh", position: "relative" }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodesDraggable={true}
          fitView
        >
          <Controls />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>

        {/* Top-right UI elements */}
        <div className="absolute top-4 right-4 z-10 flex flex-col gap-2 items-end">
          {/* FPS Display */}
          <FpsDisplay />

          {/* Action Buttons */}
          <div className="flex gap-2">
            {/* Run/Stop Button */}
            {pipelineInstanceId ? (
              <button
                onClick={handleStopPipeline}
                disabled={isStopping}
                className="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white p-2 rounded-lg shadow-lg transition-colors"
                title="Stop Pipeline"
              >
                <Square className="w-5 h-5" />
              </button>
            ) : (
              <button
                onClick={handleRunPipeline}
                disabled={isRunning}
                className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white p-2 rounded-lg shadow-lg transition-colors"
                title="Run Pipeline"
              >
                <Play className="w-5 h-5" />
              </button>
            )}

            {/* Save Button */}
            <Dialog>
              <DialogTrigger asChild>
                <button className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg shadow-lg transition-colors">
                  <Save className="w-5 h-5" />
                </button>
              </DialogTrigger>
              <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden">
                <DialogHeader>
                  <DialogTitle>Pipeline State</DialogTitle>
                  <DialogDescription>
                    Current nodes and edges state of the React Flow pipeline
                  </DialogDescription>
                </DialogHeader>
                <div className="overflow-auto max-h-[60vh]">
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-semibold mb-2">
                        Nodes ({nodes.length})
                      </h3>
                      <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-auto">
                        {JSON.stringify(nodes, null, 2)}
                      </pre>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-2">
                        Edges ({edges.length})
                      </h3>
                      <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-auto">
                        {JSON.stringify(edges, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <NodeDataPanel
          selectedNode={selectedNode}
          onNodeDataUpdate={handleNodeDataUpdate}
        />
      </div>
    );
  }

  return <div>Loading pipeline: {id}</div>;
};

export default Pipelines;
