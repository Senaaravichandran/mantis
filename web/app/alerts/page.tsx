"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { alertsAPI } from "@/lib/api-client";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getSeverityColor, formatDateTime } from "@/lib/utils";
import Link from "next/link";
import { useState } from "react";

export default function AlertsPage() {
  const queryClient = useQueryClient();
  const [severity, setSeverity] = useState<string>("");
  const [showResolved, setShowResolved] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["alerts", severity, showResolved],
    queryFn: () =>
      alertsAPI.list({
        ...(severity && { severity }),
        resolved: showResolved ? "true" : "false",
      }),
  });

  const acknowledgeMutation = useMutation({
    mutationFn: (id: string) => alertsAPI.acknowledge(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts"] }),
  });

  const resolveMutation = useMutation({
    mutationFn: (id: string) => alertsAPI.resolve(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts"] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Alerts</h2>
        <div className="flex gap-2">
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">All Severities</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
            <option value="emergency">Emergency</option>
          </select>
          <Button
            variant={showResolved ? "default" : "outline"}
            size="sm"
            onClick={() => setShowResolved(!showResolved)}
          >
            {showResolved ? "Showing Resolved" : "Show Resolved"}
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Loading alerts...</div>
      ) : data?.items?.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No alerts found
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {data?.items?.map((alert: any) => (
            <Card key={alert.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
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
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                      {alert.description}
                    </p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                      <span>Detected: {formatDateTime(alert.detected_at)}</span>
                      {alert.acknowledged && <span className="text-amber-600">Acknowledged</span>}
                      {alert.resolved && <span className="text-green-600">Resolved</span>}
                    </div>
                  </div>
                  <div className="flex gap-2 shrink-0">
                    {!alert.acknowledged && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => acknowledgeMutation.mutate(alert.id)}
                      >
                        Acknowledge
                      </Button>
                    )}
                    {!alert.resolved && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => resolveMutation.mutate(alert.id)}
                      >
                        Resolve
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {data && (
        <p className="text-sm text-gray-500">
          Showing {data.items?.length || 0} of {data.total || 0} alerts
        </p>
      )}
    </div>
  );
}
