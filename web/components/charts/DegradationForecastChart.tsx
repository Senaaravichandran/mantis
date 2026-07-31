"use client";

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";

interface ForecastPoint {
  month: number;
  health_score: number;
  confidence_low?: number;
  confidence_high?: number;
}

interface Props {
  data: ForecastPoint[];
  currentScore?: number;
  failureThreshold?: number;
  height?: number;
}

export function DegradationForecastChart({
  data,
  currentScore = 100,
  failureThreshold = 30,
  height = 300,
}: Props) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-500">
        No forecast data available
      </div>
    );
  }

  const chartData = [
    { month: 0, health_score: currentScore, confidence_low: currentScore, confidence_high: currentScore },
    ...data.map((d) => ({
      ...d,
      confidence_low: d.confidence_low ?? d.health_score * 0.85,
      confidence_high: d.confidence_high ?? Math.min(d.health_score * 1.15, 100),
    })),
  ];

  return (
    <div>
      <h4 className="text-sm font-semibold text-gray-700 mb-2">Degradation Forecast</h4>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 11 }}
            tickFormatter={(v) => `${v}mo`}
          />
          <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(v: number) => [`${v.toFixed(1)}%`, ""]}
            labelFormatter={(v) => `Month ${v}`}
            contentStyle={{ fontSize: 12 }}
          />
          <Area
            type="monotone"
            dataKey="confidence_high"
            stroke="none"
            fill="#3b82f6"
            fillOpacity={0.1}
          />
          <Area
            type="monotone"
            dataKey="confidence_low"
            stroke="none"
            fill="#ffffff"
            fillOpacity={1}
          />
          <Area
            type="monotone"
            dataKey="health_score"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.2}
            strokeWidth={2}
          />
          <ReferenceLine
            y={failureThreshold}
            stroke="#dc2626"
            strokeDasharray="5 5"
            label={{ value: "Failure Threshold", fill: "#dc2626", fontSize: 11 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
