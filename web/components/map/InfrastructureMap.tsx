"use client";

import { useEffect, useRef, useCallback } from "react";

interface Asset {
  id: string;
  name: string;
  asset_type: string;
  risk_level: string;
  latitude?: number;
  longitude?: number;
  current_health_score?: number;
}

interface Props {
  assets: Asset[];
  center?: { lat: number; lng: number };
  zoom?: number;
  onAssetClick?: (asset: Asset) => void;
  selectedAssetId?: string | null;
}

const RISK_COLORS: Record<string, string> = {
  critical: "#dc2626",
  high: "#ea580c",
  medium: "#d97706",
  low: "#16a34a",
};

const ASSET_ICONS: Record<string, string> = {
  bridge: "B",
  water_main: "W",
  road: "R",
  tunnel: "T",
  pump_station: "P",
  culvert: "C",
  retention_basin: "RB",
};

export function InfrastructureMap({
  assets,
  center = { lat: 40.4406, lng: -79.9959 },
  zoom = 12,
  onAssetClick,
  selectedAssetId,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = container.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const w = rect.width;
    const h = rect.height;

    // Water-like background
    const gradient = ctx.createLinearGradient(0, 0, w, h);
    gradient.addColorStop(0, "#e0f2fe");
    gradient.addColorStop(1, "#f0f9ff");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, w, h);

    // Grid lines (simulating streets)
    ctx.strokeStyle = "#cbd5e1";
    ctx.lineWidth = 0.5;
    for (let x = 0; x < w; x += 50) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 50) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // Draw assets
    assets.forEach((asset, i) => {
      // Distribute assets across the canvas
      const col = i % Math.ceil(Math.sqrt(assets.length));
      const row = Math.floor(i / Math.ceil(Math.sqrt(assets.length)));
      const cols = Math.ceil(Math.sqrt(assets.length));
      const rows = Math.ceil(assets.length / cols);

      const x = 50 + col * ((w - 100) / Math.max(cols - 1, 1));
      const y = 50 + row * ((h - 100) / Math.max(rows - 1, 1));

      const color = RISK_COLORS[asset.risk_level] || "#6b7280";
      const isSelected = asset.id === selectedAssetId;
      const radius = isSelected ? 18 : 14;

      // Shadow
      ctx.beginPath();
      ctx.arc(x + 1, y + 1, radius, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(0,0,0,0.1)";
      ctx.fill();

      // Main circle
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();

      if (isSelected) {
        ctx.strokeStyle = "#1e3a5f";
        ctx.lineWidth = 3;
        ctx.stroke();
      }

      // Icon letter
      ctx.fillStyle = "#ffffff";
      ctx.font = `bold ${isSelected ? 11 : 10}px sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(ASSET_ICONS[asset.asset_type] || "?", x, y);

      // Name label
      ctx.fillStyle = "#1f2937";
      ctx.font = "10px sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      const name = asset.name.length > 18 ? asset.name.slice(0, 16) + "..." : asset.name;
      ctx.fillText(name, x, y + radius + 4);
    });

    // Legend
    const legendY = h - 30;
    ctx.font = "11px sans-serif";
    ctx.textAlign = "left";
    let legendX = 10;
    Object.entries(RISK_COLORS).forEach(([level, color]) => {
      ctx.beginPath();
      ctx.arc(legendX + 6, legendY, 5, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.fillStyle = "#374151";
      ctx.fillText(level, legendX + 14, legendY + 4);
      legendX += 80;
    });
  }, [assets, selectedAssetId]);

  useEffect(() => {
    draw();
    window.addEventListener("resize", draw);
    return () => window.removeEventListener("resize", draw);
  }, [draw]);

  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || !containerRef.current || !onAssetClick) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const w = rect.width;
    const h = rect.height;

    assets.forEach((asset, i) => {
      const col = i % Math.ceil(Math.sqrt(assets.length));
      const row = Math.floor(i / Math.ceil(Math.sqrt(assets.length)));
      const cols = Math.ceil(Math.sqrt(assets.length));
      const rows = Math.ceil(assets.length / cols);

      const x = 50 + col * ((w - 100) / Math.max(cols - 1, 1));
      const y = 50 + row * ((h - 100) / Math.max(rows - 1, 1));

      if (Math.sqrt((mx - x) ** 2 + (my - y) ** 2) < 18) {
        onAssetClick(asset);
      }
    });
  };

  return (
    <div ref={containerRef} className="w-full h-full relative">
      <canvas ref={canvasRef} className="w-full h-full cursor-pointer" onClick={handleClick} />
      <div className="absolute top-2 right-2 bg-white/80 backdrop-blur-sm rounded px-2 py-1 text-xs text-gray-500">
        Canvas Map (connect Mapbox GL for production)
      </div>
    </div>
  );
}
