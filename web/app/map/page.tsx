"use client";

import { useQuery } from "@tanstack/react-query";
import { assetsAPI } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getRiskColor } from "@/lib/utils";
import { useMantisStore } from "@/lib/store";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

export default function MapPage() {
  const { data } = useQuery({
    queryKey: ["assets"],
    queryFn: () => assetsAPI.list(),
  });

  const mapCenter = useMantisStore((s) => s.mapCenter);
  const selectedAssetId = useMantisStore((s) => s.selectedAssetId);
  const setSelectedAssetId = useMantisStore((s) => s.setSelectedAssetId);
  const [hoveredAsset, setHoveredAsset] = useState<any>(null);

  const assets = data?.items || [];

  const riskCounts = {
    critical: assets.filter((a: any) => a.risk_level === "critical").length,
    high: assets.filter((a: any) => a.risk_level === "high").length,
    medium: assets.filter((a: any) => a.risk_level === "medium").length,
    low: assets.filter((a: any) => a.risk_level === "low").length,
  };

  return (
    <div className="space-y-4 h-full">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Infrastructure Map</h2>
        <div className="flex gap-2">
          {Object.entries(riskCounts).map(([level, count]) => (
            <Badge key={level} className={getRiskColor(level)} variant="outline">
              {level}: {count}
            </Badge>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4" style={{ height: "calc(100vh - 220px)" }}>
        <div className="lg:col-span-3 rounded-lg overflow-hidden border">
          <MapCanvas
            assets={assets}
            center={mapCenter}
            selectedId={selectedAssetId}
            onSelect={setSelectedAssetId}
            onHover={setHoveredAsset}
          />
        </div>

        <div className="space-y-3 overflow-y-auto">
          <Card>
            <CardHeader className="p-4">
              <CardTitle className="text-sm">Asset List</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y max-h-[60vh] overflow-y-auto">
                {assets.map((asset: any) => (
                  <button
                    key={asset.id}
                    onClick={() => setSelectedAssetId(asset.id)}
                    className={`w-full text-left p-3 hover:bg-gray-50 transition-colors ${
                      selectedAssetId === asset.id ? "bg-mantis-50 border-l-2 border-mantis-600" : ""
                    }`}
                  >
                    <p className="text-sm font-medium text-gray-900">{asset.name}</p>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-xs text-gray-500 capitalize">
                        {asset.asset_type?.replace("_", " ")}
                      </span>
                      <Badge className={getRiskColor(asset.risk_level)} variant="outline">
                        {asset.risk_level}
                      </Badge>
                    </div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {hoveredAsset && (
            <Card>
              <CardContent className="p-4">
                <h4 className="font-semibold text-sm">{hoveredAsset.name}</h4>
                <p className="text-xs text-gray-500 capitalize mt-1">
                  {hoveredAsset.asset_type?.replace("_", " ")}
                </p>
                <div className="mt-2 space-y-1 text-xs">
                  <p>Health: {hoveredAsset.current_health_score ?? "N/A"}/100</p>
                  <p>Risk: {hoveredAsset.risk_level}</p>
                </div>
                <Link
                  href={`/assets/${hoveredAsset.id}`}
                  className="text-xs text-mantis-600 hover:underline mt-2 block"
                >
                  View Details
                </Link>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

function MapCanvas({
  assets,
  center,
  selectedId,
  onSelect,
  onHover,
}: {
  assets: any[];
  center: [number, number];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onHover: (asset: any) => void;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = container.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    // Background
    ctx.fillStyle = "#e8f4f8";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Grid
    ctx.strokeStyle = "#d0e8f0";
    ctx.lineWidth = 0.5;
    for (let x = 0; x < canvas.width; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Draw assets as markers
    const riskColors: Record<string, string> = {
      critical: "#dc2626",
      high: "#ea580c",
      medium: "#d97706",
      low: "#16a34a",
    };

    assets.forEach((asset, i) => {
      const x = 60 + (i % 6) * (canvas.width - 120) / 5;
      const y = 60 + Math.floor(i / 6) * 80;

      const color = riskColors[asset.risk_level] || "#6b7280";
      const isSelected = asset.id === selectedId;

      // Marker circle
      ctx.beginPath();
      ctx.arc(x, y, isSelected ? 14 : 10, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      if (isSelected) {
        ctx.strokeStyle = "#1e40af";
        ctx.lineWidth = 3;
        ctx.stroke();
      }

      // Label
      ctx.fillStyle = "#374151";
      ctx.font = "11px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(asset.name?.slice(0, 20) || "", x, y + 24);
    });

    // Legend
    ctx.fillStyle = "#6b7280";
    ctx.font = "12px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText("Infrastructure Risk Map (connect Mapbox for full map)", 10, canvas.height - 10);
  }, [assets, center, selectedId]);

  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    assets.forEach((asset, i) => {
      const x = 60 + (i % 6) * (canvas.width - 120) / 5;
      const y = 60 + Math.floor(i / 6) * 80;
      const dist = Math.sqrt((mx - x) ** 2 + (my - y) ** 2);
      if (dist < 15) {
        onSelect(asset.id);
        onHover(asset);
      }
    });
  };

  return (
    <div ref={containerRef} className="w-full h-full bg-blue-50 relative">
      <canvas ref={canvasRef} className="w-full h-full" onClick={handleClick} />
    </div>
  );
}
