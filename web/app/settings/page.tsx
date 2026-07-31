"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SettingsPage() {
  const { data: config } = useQuery({
    queryKey: ["admin-config"],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/v1/admin/config`);
      return res.json();
    },
  });

  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/health`);
      return res.json();
    },
    refetchInterval: 30000,
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Settings</h2>

      {/* System Health */}
      <Card>
        <CardHeader>
          <CardTitle>System Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <ServiceStatus
              name="API Server"
              status={health?.status === "healthy" ? "online" : "offline"}
            />
            <ServiceStatus name="Database" status={health?.database || "unknown"} />
            <ServiceStatus name="Redis" status={health?.redis || "unknown"} />
          </div>
        </CardContent>
      </Card>

      {/* Platform Info */}
      <Card>
        <CardHeader>
          <CardTitle>Platform Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <ConfigRow label="Version" value={config?.version || "1.0.0"} />
            <ConfigRow label="API URL" value={API_URL} />
            <ConfigRow
              label="AI Agents"
              value={config?.agents?.join(", ") || "sentinel, analyst, planner, reporter, contractor, regulator"}
            />
            <ConfigRow
              label="Asset Types"
              value={config?.asset_types?.join(", ") || "bridge, water_main, road, tunnel, pump_station, culvert, retention_basin"}
            />
            <ConfigRow
              label="Sensor Types"
              value={config?.sensor_types?.join(", ") || "vibration, strain, temperature, water_level, flow_rate, pressure, displacement, corrosion, humidity, ph"}
            />
          </div>
        </CardContent>
      </Card>

      {/* Environment */}
      <Card>
        <CardHeader>
          <CardTitle>Environment Variables</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <p className="text-gray-500">
              Environment variables are configured in <code className="bg-gray-100 px-1 rounded">.env</code> file.
              Restart services after changes.
            </p>
            <div className="grid grid-cols-1 gap-2 mt-4">
              {[
                { key: "NEXT_PUBLIC_API_URL", desc: "Backend API URL" },
                { key: "NEXT_PUBLIC_WS_URL", desc: "WebSocket URL" },
                { key: "NEXT_PUBLIC_MAPBOX_TOKEN", desc: "Mapbox GL Token" },
                { key: "POSTGRES_*", desc: "Database connection" },
                { key: "REDIS_URL", desc: "Redis connection" },
                { key: "KAFKA_BOOTSTRAP_SERVERS", desc: "Kafka brokers" },
                { key: "OLLAMA_HOST", desc: "Ollama LLM server" },
              ].map((env) => (
                <div key={env.key} className="flex items-center gap-3 rounded border p-2">
                  <code className="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded">{env.key}</code>
                  <span className="text-xs text-gray-500">{env.desc}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function ServiceStatus({ name, status }: { name: string; status: string }) {
  const isOnline = status === "online" || status === "healthy" || status === "connected";
  return (
    <div className="flex items-center gap-3 rounded-lg border p-4">
      <div className={`h-3 w-3 rounded-full ${isOnline ? "bg-green-500" : "bg-red-500"}`} />
      <div>
        <p className="text-sm font-medium text-gray-900">{name}</p>
        <p className="text-xs text-gray-500 capitalize">{status}</p>
      </div>
    </div>
  );
}

function ConfigRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start gap-4 text-sm">
      <span className="w-32 shrink-0 font-medium text-gray-500">{label}</span>
      <span className="text-gray-900">{value}</span>
    </div>
  );
}
