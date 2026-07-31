"use client";

import { useQuery } from "@tanstack/react-query";
import { assetsAPI } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getRiskColor, formatDate } from "@/lib/utils";
import Link from "next/link";
import { useState } from "react";

export default function AssetsPage() {
  const [filter, setFilter] = useState<string>("");

  const { data, isLoading } = useQuery({
    queryKey: ["assets", filter],
    queryFn: () => assetsAPI.list(filter ? { asset_type: filter } : undefined),
  });

  const assetTypes = ["bridge", "water_main", "road", "tunnel", "pump_station", "culvert", "retention_basin"];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Infrastructure Assets</h2>
        <div className="flex gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">All Types</option>
            {assetTypes.map((t) => (
              <option key={t} value={t}>{t.replace("_", " ")}</option>
            ))}
          </select>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Material</TableHead>
                <TableHead>Health</TableHead>
                <TableHead>Risk</TableHead>
                <TableHead>Last Inspection</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow><TableCell colSpan={6} className="text-center py-8 text-gray-500">Loading...</TableCell></TableRow>
              ) : data?.items?.length === 0 ? (
                <TableRow><TableCell colSpan={6} className="text-center py-8 text-gray-500">No assets found</TableCell></TableRow>
              ) : (
                data?.items?.map((asset: any) => (
                  <TableRow key={asset.id}>
                    <TableCell>
                      <Link href={`/assets/${asset.id}`} className="font-medium text-mantis-600 hover:underline">
                        {asset.name}
                      </Link>
                    </TableCell>
                    <TableCell className="capitalize">{asset.asset_type.replace("_", " ")}</TableCell>
                    <TableCell>{asset.material || "-"}</TableCell>
                    <TableCell>
                      <HealthBar score={asset.current_health_score} />
                    </TableCell>
                    <TableCell>
                      <Badge className={getRiskColor(asset.risk_level)}>{asset.risk_level}</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-gray-500">
                      {asset.last_inspection_date ? formatDate(asset.last_inspection_date) : "Never"}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {data && (
        <p className="text-sm text-gray-500">
          Showing {data.items?.length || 0} of {data.total || 0} assets
        </p>
      )}
    </div>
  );
}

function HealthBar({ score }: { score: number | null }) {
  if (score === null || score === undefined) return <span className="text-gray-400">-</span>;
  const color = score >= 70 ? "bg-green-500" : score >= 40 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-sm">{Math.round(score)}</span>
    </div>
  );
}
