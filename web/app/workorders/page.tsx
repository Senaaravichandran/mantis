"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { workOrdersAPI } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getStatusColor, formatDate, formatCurrency } from "@/lib/utils";
import Link from "next/link";
import { useState } from "react";

const STATUS_COLUMNS = [
  { key: "draft", label: "Draft" },
  { key: "pending_approval", label: "Pending Approval" },
  { key: "approved", label: "Approved" },
  { key: "in_progress", label: "In Progress" },
  { key: "completed", label: "Completed" },
];

export default function WorkOrdersPage() {
  const queryClient = useQueryClient();
  const [viewMode, setViewMode] = useState<"kanban" | "list">("kanban");

  const { data, isLoading } = useQuery({
    queryKey: ["workorders"],
    queryFn: () => workOrdersAPI.list(),
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => workOrdersAPI.approve(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["workorders"] }),
  });

  const workOrders = data?.items || [];

  const getOrdersByStatus = (status: string) =>
    workOrders.filter((wo: any) => wo.status === status);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Work Orders</h2>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant={viewMode === "kanban" ? "default" : "outline"}
            onClick={() => setViewMode("kanban")}
          >
            Kanban
          </Button>
          <Button
            size="sm"
            variant={viewMode === "list" ? "default" : "outline"}
            onClick={() => setViewMode("list")}
          >
            List
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Loading work orders...</div>
      ) : viewMode === "kanban" ? (
        <div className="flex gap-4 overflow-x-auto pb-4">
          {STATUS_COLUMNS.map((col) => {
            const items = getOrdersByStatus(col.key);
            return (
              <div key={col.key} className="min-w-[280px] flex-1">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-gray-700">{col.label}</h3>
                  <span className="text-xs text-gray-400">{items.length}</span>
                </div>
                <div className="space-y-3">
                  {items.map((wo: any) => (
                    <Card key={wo.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-3">
                        <Link href={`/workorders/${wo.id}`} className="block">
                          <p className="text-sm font-medium text-gray-900 mb-1">
                            {wo.title}
                          </p>
                          <p className="text-xs text-gray-500 line-clamp-2">{wo.scope}</p>
                          <div className="flex items-center justify-between mt-2">
                            <Badge className={getStatusColor(wo.priority)} variant="outline">
                              {wo.priority}
                            </Badge>
                            {wo.estimated_cost && (
                              <span className="text-xs font-medium text-gray-600">
                                {formatCurrency(wo.estimated_cost)}
                              </span>
                            )}
                          </div>
                        </Link>
                        {wo.status === "pending_approval" && (
                          <Button
                            size="sm"
                            className="mt-2 w-full"
                            onClick={() => approveMutation.mutate(wo.id)}
                          >
                            Approve
                          </Button>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                  {items.length === 0 && (
                    <div className="rounded-lg border-2 border-dashed border-gray-200 p-6 text-center">
                      <p className="text-xs text-gray-400">No items</p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="divide-y">
              {workOrders.map((wo: any) => (
                <div key={wo.id} className="flex items-center gap-4 p-4 hover:bg-gray-50">
                  <div className="flex-1 min-w-0">
                    <Link href={`/workorders/${wo.id}`} className="text-sm font-medium text-gray-900 hover:text-mantis-600">
                      {wo.title}
                    </Link>
                    <p className="text-xs text-gray-500 mt-1">{wo.scope?.slice(0, 100)}</p>
                  </div>
                  <Badge className={getStatusColor(wo.status)} variant="outline">
                    {wo.status?.replace(/_/g, " ")}
                  </Badge>
                  <Badge className={getStatusColor(wo.priority)} variant="outline">
                    {wo.priority}
                  </Badge>
                  {wo.estimated_cost && (
                    <span className="text-sm font-medium text-gray-600 w-24 text-right">
                      {formatCurrency(wo.estimated_cost)}
                    </span>
                  )}
                  <span className="text-xs text-gray-400 w-24 text-right">
                    {wo.due_date ? formatDate(wo.due_date) : "No date"}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {data && (
        <p className="text-sm text-gray-500">
          Showing {data.items?.length || 0} of {data.total || 0} work orders
        </p>
      )}
    </div>
  );
}
