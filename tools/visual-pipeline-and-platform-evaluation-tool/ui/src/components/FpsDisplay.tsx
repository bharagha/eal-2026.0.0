import { useState } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { Cpu, Gauge, Gpu } from "lucide-react";

interface FpsDisplayProps {
  className?: string;
}

const FpsDisplay = ({ className = "" }: FpsDisplayProps) => {
  const [lastMessage, setLastMessage] = useState<string>("");

  const { readyState } = useWebSocket(
    "ws://10.123.233.214:7860/metrics/ws/clients",
    {
      onOpen: () => {
        console.log("WebSocket connected");
      },
      onMessage: (event) => {
        setLastMessage(event.data);
      },
      onError: (error) => {
        console.error("WebSocket error:", error);
      },
      onClose: () => {
        console.log("WebSocket disconnected");
      },
      shouldReconnect: () => true, // Automatically reconnect on close
    },
  );

  const getStatusColor = () => {
    switch (readyState) {
      case ReadyState.OPEN:
        return "text-green-600";
      case ReadyState.CONNECTING:
        return "text-yellow-600";
      case ReadyState.CLOSING:
      case ReadyState.CLOSED:
      case ReadyState.UNINSTANTIATED:
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getStatusIcon = () => {
    switch (readyState) {
      case ReadyState.OPEN:
        return "●";
      case ReadyState.CONNECTING:
        return "○";
      case ReadyState.CLOSING:
      case ReadyState.CLOSED:
      case ReadyState.UNINSTANTIATED:
        return "●";
      default:
        return "○";
    }
  };

  const parseMessage = (msg: string): [string, string, string] | null => {
    if (msg === "") return null;
    const json = JSON.parse(msg);
    console.log(json);
    if ("metrics" in json) {
      const fps =
        json.metrics.find((m) => m.name === "fps")?.fields?.value ?? "0";
      const cpu =
        json.metrics.find((m) => m.name === "cpu")?.fields?.usage_user ?? "0";
      const gpu =
        json.metrics.find(
          (m) => m.name === "gpu_engine_usage" && m.fields.usage > 0,
        )?.fields?.usage ?? "0";
      return [fps, cpu, gpu];
    }
    return null;
  };

  const metrics = parseMessage(lastMessage);

  return (
    <div
      className={`bg-black/80 text-white p-2 rounded-lg shadow-lg text-sm ${className}`}
    >
      <div className="flex flex-row gap-2 font-mono justify-center items-center">
        <span className={getStatusColor()}>{getStatusIcon()}</span>
        {metrics && (
          <>
            <Gauge />
            {metrics[0]}
            <Cpu />
            {parseFloat(metrics[1]).toFixed(2)}%
            <Gpu />
            {parseFloat(metrics[2]).toFixed(2)}%
          </>
        )}
        {!metrics && "No messages"}
      </div>
    </div>
  );
};

export default FpsDisplay;
