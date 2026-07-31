"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { agentsAPI } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDateTime } from "@/lib/utils";

export default function AgentRunDetailPage() {
  const params = useParams();
  const runId = params.runId as string;

  const { data: run, isLoading } = useQuery({
    queryKey: ["agent-run", runId],
    queryFn: () => agentsAPI.getRun(runId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "running" || status === "queued" ? 3000 : false;
    },
  });

  if (isLoading) return <div className="text-gray-500">Loading agent run...</div>;
  if (!run) return <div className="text-red-500">Agent run not found</div>;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-800";
      case "running": return "bg-blue-100 text-blue-800 animate-pulse";
      case "queued": return "bg-amber-100 text-amber-800";
      case "failed": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const thoughtChain = run.result?.thought_chain || run.thought_chain || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 capitalize">
            {run.agent_type} Agent Run
          </h2>
          <p className="text-sm text-gray-500">Run ID: {run.id}</p>
        </div>
        <Badge className={getStatusColor(run.status)}>{run.status}</Badge>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <InfoCard label="Agent Type" value={run.agent_type} />
        <InfoCard label="Trigger" value={run.trigger_type} />
        <InfoCard label="Started" value={run.started_at ? formatDateTime(run.started_at) : "Queued"} />
        <InfoCard label="Duration" value={run.duration_seconds ? `${run.duration_seconds.toFixed(1)}s` : "In progress..."} />
      </div>

      {/* Thought Chain */}
      <Card>
        <CardHeader>
          <CardTitle>Agent Thought Chain</CardTitle>
        </CardHeader>
        <CardContent>
          {thoughtChain.length > 0 ? (
            <div className="space-y-4">
              {thoughtChain.map((thought: any, i: number) => (
                <div key={i} className="relative pl-8 pb-4 border-l-2 border-mantis-200 last:border-0">
                  <div className="absolute -left-2 top-0 h-4 w-4 rounded-full bg-mantis-600" />
                  <div className="rounded-lg border p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-semibold text-mantis-700 capitalize">
                        {thought.agent || `Step ${i + 1}`}
                      </span>
                      {thought.timestamp && (
                        <span className="text-xs text-gray-400">
                          {formatDateTime(thought.timestamp)}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">
                      {thought.thought || thought.content || JSON.stringify(thought)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">
              {run.status === "running" || run.status === "queued"
                ? "Waiting for agent reasoning..."
                : "No thought chain recorded for this run."}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Result */}
      {run.result && (
        <Card>
          <CardHeader>
            <CardTitle>Run Result</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
              {JSON.stringify(run.result, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}

      {run.error && (
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="text-red-700">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-sm text-red-600 bg-red-50 p-4 rounded-lg overflow-auto">
              {run.error}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-xs font-medium text-gray-500">{label}</p>
        <p className="text-lg font-bold text-gray-900 mt-1 capitalize">{value}</p>
      </CardContent>
    </Card>
  );
}
