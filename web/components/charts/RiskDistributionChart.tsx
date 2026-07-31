"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface Props {
  data: Record<string, number>;
  height?: number;
}

const RISK_COLORS: Record<string, string> = {
  low: "#16a34a",
  medium: "#f59e0b",
  high: "#ef4444",
  critical: "#991b1b",
};

export function RiskDistributionChart({ data, height = 250 }: Props) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-500">
        No risk data available
      </div>
    );
  }

  const chartData = Object.entries(data).map(([level, count]) => ({
    name: level.charAt(0).toUpperCase() + level.slice(1),
    count,
    level,
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
        <Tooltip contentStyle={{ fontSize: 12 }} />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {chartData.map((entry) => (
            <Cell key={entry.level} fill={RISK_COLORS[entry.level] || "#6b7280"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
