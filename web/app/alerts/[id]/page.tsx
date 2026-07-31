"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { alertsAPI, assetsAPI } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getSeverityColor, formatDateTime } from "@/lib/utils";

export default function AlertDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const queryClient = useQueryClient();

  const { data: alert, isLoading } = useQuery({
    queryKey: ["alert", id],
    queryFn: () => alertsAPI.get(id),
  });

  const { data: asset } = useQuery({
    queryKey: ["asset", alert?.asset_id],
    queryFn: () => assetsAPI.get(alert.asset_id),
    enabled: !!alert?.asset_id,
  });

  const acknowledgeMutation = useMutation({
    mutationFn: () => alertsAPI.acknowledge(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alert", id] }),
  });

  const resolveMutation = useMutation({
    mutationFn: () => alertsAPI.resolve(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alert", id] }),
  });

  if (isLoading) return <div className="text-gray-500">Loading alert...</div>;
  if (!alert) return <div className="text-red-500">Alert not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{alert.title}</h2>
          <p className="text-sm text-gray-500">Alert ID: {alert.id}</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge className={getSeverityColor(alert.severity)} variant="outline">
            {alert.severity}
          </Badge>
          {!alert.acknowledged && (
            <Button size="sm" variant="outline" onClick={() => acknowledgeMutation.mutate()}>
              Acknowledge
            </Button>
          )}
          {!alert.resolved && (
            <Button size="sm" onClick={() => resolveMutation.mutate()}>
              Resolve
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <InfoCard label="Severity" value={alert.severity} />
        <InfoCard label="Detected" value={formatDateTime(alert.detected_at)} />
        <InfoCard label="Status" value={alert.resolved ? "Resolved" : alert.acknowledged ? "Acknowledged" : "Active"} />
        <InfoCard label="Asset" value={asset?.name || alert.asset_id || "N/A"} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Description</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{alert.description || "No description provided."}</p>
        </CardContent>
      </Card>

      {alert.agent_reasoning && (
        <Card>
          <CardHeader>
            <CardTitle>Agent Reasoning</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {typeof alert.agent_reasoning === "string" ? (
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{alert.agent_reasoning}</p>
              ) : (
                <pre className="text-sm bg-gray-50 p-4 rounded-lg overflow-auto">
                  {JSON.stringify(alert.agent_reasoning, null, 2)}
                </pre>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {alert.sensor_snapshot && (
        <Card>
          <CardHeader>
            <CardTitle>Sensor Snapshot at Detection</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {Object.entries(alert.sensor_snapshot as Record<string, any>).map(([key, val]) => (
                <div key={key} className="rounded-lg border p-3">
                  <p className="text-xs text-gray-500 capitalize">{key.replace(/_/g, " ")}</p>
                  <p className="text-lg font-bold text-gray-900">{String(val)}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <TimelineItem label="Detected" time={alert.detected_at} active />
            {alert.acknowledged_at && (
              <TimelineItem label="Acknowledged" time={alert.acknowledged_at} />
            )}
            {alert.resolved_at && (
              <TimelineItem label="Resolved" time={alert.resolved_at} />
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-xs font-medium text-gray-500">{label}</p>
        <p className="text-lg font-bold text-gray-900 mt-1 capitalize">{value}</p>
      </CardContent>
    </Card>
  );
}

function TimelineItem({ label, time, active = false }: { label: string; time: string; active?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div className={`h-3 w-3 rounded-full ${active ? "bg-mantis-600" : "bg-gray-300"}`} />
      <div>
        <p className="text-sm font-medium text-gray-900">{label}</p>
        <p className="text-xs text-gray-500">{formatDateTime(time)}</p>
      </div>
    </div>
  );
}
