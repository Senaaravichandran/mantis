"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface SensorReading {
  time: string;
  value: number;
  sensor_type: string;
  unit?: string;
}

interface Props {
  data: SensorReading[];
  title?: string;
  height?: number;
}

const SENSOR_COLORS: Record<string, string> = {
  vibration: "#3b82f6",
  strain: "#ef4444",
  temperature: "#f59e0b",
  water_level: "#06b6d4",
  flow_rate: "#8b5cf6",
  pressure: "#ec4899",
  displacement: "#10b981",
  corrosion: "#f97316",
  humidity: "#6366f1",
  ph: "#14b8a6",
};

export function SensorTimeSeriesChart({ data, title, height = 300 }: Props) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-500">
        No sensor data available
      </div>
    );
  }

  // Group by sensor type
  const sensorTypes = [...new Set(data.map((d) => d.sensor_type))];

  // Transform data for recharts: pivot by time
  const timeMap = new Map<string, Record<string, number>>();
  data.forEach((reading) => {
    const key = reading.time;
    if (!timeMap.has(key)) timeMap.set(key, { time: new Date(key).getTime() } as any);
    const entry = timeMap.get(key)!;
    entry[reading.sensor_type] = reading.value;
  });

  const chartData = Array.from(timeMap.values()).sort((a: any, b: any) => a.time - b.time);

  return (
    <div>
      {title && <h4 className="text-sm font-semibold text-gray-700 mb-2">{title}</h4>}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="time"
            type="number"
            domain={["dataMin", "dataMax"]}
            tickFormatter={(v) => new Date(v).toLocaleDateString()}
            tick={{ fontSize: 11 }}
          />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip
            labelFormatter={(v) => new Date(v).toLocaleString()}
            contentStyle={{ fontSize: 12 }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {sensorTypes.map((type) => (
            <Line
              key={type}
              type="monotone"
              dataKey={type}
              stroke={SENSOR_COLORS[type] || "#6b7280"}
              strokeWidth={2}
              dot={false}
              name={type.replace(/_/g, " ")}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
