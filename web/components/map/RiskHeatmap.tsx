"use client";

import { useEffect, useRef } from "react";

interface HeatmapPoint {
  lat: number;
  lng: number;
  intensity: number;
}

interface Props {
  points: HeatmapPoint[];
  width?: number;
  height?: number;
}

export function RiskHeatmap({ points, width = 600, height = 400 }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || points.length === 0) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = width;
    canvas.height = height;

    // Background
    ctx.fillStyle = "#f0f9ff";
    ctx.fillRect(0, 0, width, height);

    // Normalize points to canvas
    const lats = points.map((p) => p.lat);
    const lngs = points.map((p) => p.lng);
    const minLat = Math.min(...lats);
    const maxLat = Math.max(...lats);
    const minLng = Math.min(...lngs);
    const maxLng = Math.max(...lngs);

    const padding = 40;
    const mapW = width - padding * 2;
    const mapH = height - padding * 2;

    points.forEach((point) => {
      const x = padding + ((point.lng - minLng) / (maxLng - minLng || 1)) * mapW;
      const y = padding + ((maxLat - point.lat) / (maxLat - minLat || 1)) * mapH;
      const radius = 30 + point.intensity * 20;

      const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
      const alpha = Math.min(point.intensity * 0.4, 0.6);

      if (point.intensity > 0.7) {
        gradient.addColorStop(0, `rgba(220, 38, 38, ${alpha})`);
        gradient.addColorStop(1, "rgba(220, 38, 38, 0)");
      } else if (point.intensity > 0.4) {
        gradient.addColorStop(0, `rgba(245, 158, 11, ${alpha})`);
        gradient.addColorStop(1, "rgba(245, 158, 11, 0)");
      } else {
        gradient.addColorStop(0, `rgba(22, 163, 74, ${alpha})`);
        gradient.addColorStop(1, "rgba(22, 163, 74, 0)");
      }

      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.fill();
    });
  }, [points, width, height]);

  if (points.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-500">
        No heatmap data available
      </div>
    );
  }

  return <canvas ref={canvasRef} className="rounded-lg border" />;
}
