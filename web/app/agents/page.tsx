"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { agentsAPI } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatDateTime } from "@/lib/utils";
import Link from "next/link";
import { useState } from "react";

const AGENT_TYPES = [
  { value: "sentinel", label: "Sentinel", desc: "Anomaly Detection" },
  { value: "analyst", label: "Analyst", desc: "Risk Scoring" },
  { value: "planner", label: "Planner", desc: "Maintenance Planning" },
  { value: "reporter", label: "Reporter", desc: "Report Generation" },
  { value: "contractor", label: "Contractor", desc: "RFQ Management" },
  { value: "regulator", label: "Regulator", desc: "Compliance Monitoring" },
];

export default function AgentsPage() {
  const queryClient = useQueryClient();
  const [triggerAgent, setTriggerAgent] = useState("sentinel");

  const { data, isLoading } = useQuery({
    queryKey: ["agent-runs"],
    queryFn: () => agentsAPI.list(),
    refetchInterval: 10000,
  });

  const triggerMutation = useMutation({
    mutationFn: (agentType: string) =>
      agentsAPI.trigger({ agent_type: agentType, trigger_type: "manual" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["agent-runs"] }),
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-800";
      case "running": return "bg-blue-100 text-blue-800";
      case "queued": return "bg-amber-100 text-amber-800";
      case "failed": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Agent Runs</h2>
      </div>

      {/* Agent Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {AGENT_TYPES.map((agent) => (
          <Card key={agent.value} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-gray-900">{agent.label}</p>
                  <p className="text-xs text-gray-500">{agent.desc}</p>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => triggerMutation.mutate(agent.value)}
                  disabled={triggerMutation.isPending}
                >
                  Trigger
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Run History */}
      <Card>
        <CardHeader>
          <CardTitle>Run History</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Agent</TableHead>
                <TableHead>Trigger</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Started</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : !data?.items?.length ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                    No agent runs yet
                  </TableCell>
                </TableRow>
              ) : (
                data.items.map((run: any) => (
                  <TableRow key={run.id}>
                    <TableCell className="font-medium capitalize">{run.agent_type}</TableCell>
                    <TableCell className="text-sm capitalize">{run.trigger_type}</TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(run.status)}>{run.status}</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-gray-500">
                      {formatDateTime(run.started_at)}
                    </TableCell>
                    <TableCell className="text-sm text-gray-500">
                      {run.duration_seconds ? `${run.duration_seconds.toFixed(1)}s` : "-"}
                    </TableCell>
                    <TableCell>
                      <Link
                        href={`/agents/${run.id}`}
                        className="text-sm text-mantis-600 hover:underline"
                      >
                        View
                      </Link>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
