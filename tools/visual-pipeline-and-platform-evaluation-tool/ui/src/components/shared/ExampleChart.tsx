import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid } from "recharts";

const chartData = [
  { time: "00:00", cpu: 45, gpu: 30 },
  { time: "00:05", cpu: 52, gpu: 48 },
  { time: "00:10", cpu: 61, gpu: 55 },
  { time: "00:15", cpu: 48, gpu: 42 },
  { time: "00:20", cpu: 72, gpu: 68 },
  { time: "00:25", cpu: 65, gpu: 71 },
  { time: "00:30", cpu: 58, gpu: 52 },
];

const chartConfig = {
  cpu: {
    label: "CPU Usage",
    color: "var(--chart-1)",
  },
  gpu: {
    label: "GPU Usage",
    color: "var(--chart-2)",
  },
} satisfies ChartConfig;

export const ExampleChart = () => {
  return (
    <div className="w-full max-w-2xl p-4">
      <h3 className="mb-4 text-lg font-semibold">System Usage Over Time</h3>
      <ChartContainer config={chartConfig} className="h-[300px] w-full">
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} tickFormatter={(v) => `${v}%`} />
          <ChartTooltip content={<ChartTooltipContent />} />
          <ChartLegend content={<ChartLegendContent />} />
          <Area
            type="monotone"
            dataKey="cpu"
            stroke="var(--color-cpu)"
            fill="var(--color-cpu)"
            fillOpacity={0.3}
          />
          <Area
            type="monotone"
            dataKey="gpu"
            stroke="var(--color-gpu)"
            fill="var(--color-gpu)"
            fillOpacity={0.3}
          />
        </AreaChart>
      </ChartContainer>
    </div>
  );
};
