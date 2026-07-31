"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { workOrdersAPI, assetsAPI } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getStatusColor, formatDate, formatDateTime, formatCurrency } from "@/lib/utils";

export default function WorkOrderDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const queryClient = useQueryClient();

  const { data: wo, isLoading } = useQuery({
    queryKey: ["workorder", id],
    queryFn: () => workOrdersAPI.get(id),
  });

  const { data: asset } = useQuery({
    queryKey: ["asset", wo?.asset_id],
    queryFn: () => assetsAPI.get(wo.asset_id),
    enabled: !!wo?.asset_id,
  });

  const approveMutation = useMutation({
    mutationFn: () => workOrdersAPI.approve(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["workorder", id] }),
  });

  if (isLoading) return <div className="text-gray-500">Loading work order...</div>;
  if (!wo) return <div className="text-red-500">Work order not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{wo.title}</h2>
          <p className="text-sm text-gray-500">Work Order #{wo.id?.slice(0, 8)}</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge className={getStatusColor(wo.status)} variant="outline">
            {wo.status?.replace(/_/g, " ")}
          </Badge>
          <Badge className={getStatusColor(wo.priority)} variant="outline">
            Priority: {wo.priority}
          </Badge>
          {wo.status === "pending_approval" && (
            <Button onClick={() => approveMutation.mutate()}>Approve</Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <InfoCard label="Asset" value={asset?.name || wo.asset_id || "N/A"} />
        <InfoCard label="Estimated Cost" value={wo.estimated_cost ? formatCurrency(wo.estimated_cost) : "TBD"} />
        <InfoCard label="Due Date" value={wo.due_date ? formatDate(wo.due_date) : "Not set"} />
        <InfoCard label="Created" value={formatDateTime(wo.created_at)} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Scope of Work</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">
            {wo.scope || "No scope defined."}
          </p>
        </CardContent>
      </Card>

      {wo.materials && wo.materials.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Materials Required</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {wo.materials.map((mat: any, i: number) => (
                <li key={i} className="flex items-center justify-between rounded border p-2 text-sm">
                  <span>{mat.name || mat}</span>
                  {mat.quantity && <span className="text-gray-500">Qty: {mat.quantity}</span>}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {wo.contractor_id && (
        <Card>
          <CardHeader>
            <CardTitle>Assigned Contractor</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700">Contractor ID: {wo.contractor_id}</p>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Status Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <TimelineItem label="Created" time={wo.created_at} active />
            {wo.approved_at && <TimelineItem label="Approved" time={wo.approved_at} />}
            {wo.started_at && <TimelineItem label="Work Started" time={wo.started_at} />}
            {wo.completed_at && <TimelineItem label="Completed" time={wo.completed_at} />}
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
        <p className="text-lg font-bold text-gray-900 mt-1">{value}</p>
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
