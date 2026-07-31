"use client";

import { Badge } from "@/components/ui/badge";
import { getRiskColor } from "@/lib/utils";
import Link from "next/link";

interface Asset {
  id: string;
  name: string;
  asset_type: string;
  risk_level: string;
  current_health_score?: number | null;
  material?: string;
}

interface Props {
  asset: Asset;
  onClose?: () => void;
}

export function AssetPopup({ asset, onClose }: Props) {
  return (
    <div className="bg-white rounded-lg shadow-lg border p-4 min-w-[200px] max-w-[280px]">
      <div className="flex items-start justify-between mb-2">
        <h4 className="text-sm font-semibold text-gray-900">{asset.name}</h4>
        {onClose && (
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-lg leading-none">
            &times;
          </button>
        )}
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500 capitalize">
            {asset.asset_type?.replace(/_/g, " ")}
          </span>
          <Badge className={getRiskColor(asset.risk_level)} variant="outline">
            {asset.risk_level}
          </Badge>
        </div>

        {asset.current_health_score !== null && asset.current_health_score !== undefined && (
          <div>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-gray-500">Health</span>
              <span className="font-medium">{Math.round(asset.current_health_score)}/100</span>
            </div>
            <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  asset.current_health_score >= 70
                    ? "bg-green-500"
                    : asset.current_health_score >= 40
                    ? "bg-amber-500"
                    : "bg-red-500"
                }`}
                style={{ width: `${asset.current_health_score}%` }}
              />
            </div>
          </div>
        )}

        {asset.material && (
          <p className="text-xs text-gray-500">Material: {asset.material}</p>
        )}

        <Link
          href={`/assets/${asset.id}`}
          className="block text-xs text-center text-mantis-600 hover:underline mt-2 pt-2 border-t"
        >
          View Full Details
        </Link>
      </div>
    </div>
  );
}
