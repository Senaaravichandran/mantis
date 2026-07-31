"use client";

import { getSeverityColor } from "@/lib/utils";

interface Props {
  severity: string;
  count?: number;
  showDot?: boolean;
}

export function AlertBadge({ severity, count, showDot = true }: Props) {
  const colorClass = getSeverityColor(severity);

  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${colorClass}`}>
      {showDot && (
        <span
          className={`h-1.5 w-1.5 rounded-full ${
            severity === "emergency" || severity === "critical"
              ? "bg-red-500 animate-pulse"
              : severity === "warning"
              ? "bg-amber-500"
              : "bg-blue-500"
          }`}
        />
      )}
      {severity}
      {count !== undefined && count > 0 && (
        <span className="ml-0.5 font-bold">({count})</span>
      )}
    </span>
  );
}
