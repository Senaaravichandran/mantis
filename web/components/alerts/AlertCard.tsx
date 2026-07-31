"use client";

import { Badge } from "@/components/ui/badge";
import { getSeverityColor, formatDateTime } from "@/lib/utils";
import Link from "next/link";

interface Alert {
  id: string;
  title: string;
  description?: string;
  severity: string;
  detected_at: string;
  acknowledged?: boolean;
  resolved?: boolean;
  asset_id?: string;
}

interface Props {
  alert: Alert;
  compact?: boolean;
}

export function AlertCard({ alert, compact = false }: Props) {
  return (
    <div className={`rounded-lg border p-${compact ? 3 : 4} hover:shadow-md transition-shadow`}>
      <div className="flex items-start gap-3">
        <Badge className={getSeverityColor(alert.severity)}>
          {alert.severity}
        </Badge>
        <div className="flex-1 min-w-0">
          <Link
            href={`/alerts/${alert.id}`}
            className="text-sm font-semibold text-gray-900 hover:text-mantis-600"
          >
            {alert.title}
          </Link>
          {!compact && alert.description && (
            <p className="text-xs text-gray-500 mt-1 line-clamp-2">{alert.description}</p>
          )}
          <div className="flex items-center gap-3 mt-1">
            <span className="text-xs text-gray-400">{formatDateTime(alert.detected_at)}</span>
            {alert.acknowledged && !alert.resolved && (
              <span className="text-xs text-amber-600 font-medium">Acknowledged</span>
            )}
            {alert.resolved && (
              <span className="text-xs text-green-600 font-medium">Resolved</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
