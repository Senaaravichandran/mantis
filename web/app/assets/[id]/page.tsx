"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { assetsAPI, sensorsAPI, alertsAPI } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getRiskColor, getSeverityColor, formatDate, formatDateTime } from "@/lib/utils";

export default function AssetDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: asset, isLoading } = useQuery({
    queryKey: ["asset", id],
    queryFn: () => assetsAPI.get(id),
  });

  const { data: sensorData } = useQuery({
    queryKey: ["sensors", id],
    queryFn: () => sensorsAPI.history(id, 7),
    enabled: !!id,
  });

  const { data: alerts } = useQuery({
    queryKey: ["asset-alerts", id],
    queryFn: () => alertsAPI.list({ asset_id: id }),
    enabled: !!id,
  });

  if (isLoading) return <div className="text-gray-500">Loading asset details...</div>;
  if (!asset) return <div className="text-red-500">Asset not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{asset.name}</h2>
          <p className="text-sm text-gray-500 capitalize">{asset.asset_type?.replace("_", " ")} | {asset.material || "Unknown material"}</p>
        </div>
        <Badge className={getRiskColor(asset.risk_level)} variant="outline">
          Risk: {asset.risk_level}
        </Badge>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Health Score" value={`${asset.current_health_score ?? 'N/A'}/100`} />
        <MetricCard label="Installation" value={asset.installation_date ? formatDate(asset.installation_date) : "Unknown"} />
        <MetricCard label="Last Inspection" value={asset.last_inspection_date ? formatDate(asset.last_inspection_date) : "Never"} />
        <MetricCard label="Active Alerts" value={`${alerts?.total || 0}`} />
      </div>

      {/* Sensor Data */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Sensor Readings</CardTitle>
        </CardHeader>
        <CardContent>
          {sensorData && sensorData.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {sensorData.slice(0, 20).map((reading: any, i: number) => (
                <div key={i} className="flex items-center justify-between rounded border p-2 text-sm">
                  <span className="font-medium capitalize">{reading.sensor_type}</span>
                  <span>{reading.value} {reading.unit}</span>
                  <span className="text-gray-500">{formatDateTime(reading.time)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No sensor data available</p>
          )}
        </CardContent>
      </Card>

      {/* Alerts */}
      <Card>
        <CardHeader>
          <CardTitle>Alerts History</CardTitle>
        </CardHeader>
        <CardContent>
          {alerts?.items?.length > 0 ? (
            <div className="space-y-3">
              {alerts.items.map((alert: any) => (
                <div key={alert.id} className="flex items-start gap-3 rounded-lg border p-3">
                  <Badge className={getSeverityColor(alert.severity)}>{alert.severity}</Badge>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{alert.title}</p>
                    <p className="text-xs text-gray-500 mt-1">{alert.description?.slice(0, 150)}...</p>
                    <p className="text-xs text-gray-400 mt-1">{formatDateTime(alert.detected_at)}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No alerts for this asset</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-xs font-medium text-gray-500">{label}</p>
        <p className="text-lg font-bold text-gray-900 mt-1">{value}</p>
      </CardContent>
    </Card>
  );
}
