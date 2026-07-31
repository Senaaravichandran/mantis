"use client";

interface Props {
  status: string;
  agentType?: string;
  duration?: number;
  showLabel?: boolean;
}

export function AgentRunStatus({ status, agentType, duration, showLabel = true }: Props) {
  const getStatusConfig = (s: string) => {
    switch (s) {
      case "completed":
        return { color: "bg-green-500", label: "Completed", animate: false };
      case "running":
        return { color: "bg-blue-500", label: "Running", animate: true };
      case "queued":
        return { color: "bg-amber-500", label: "Queued", animate: true };
      case "failed":
        return { color: "bg-red-500", label: "Failed", animate: false };
      default:
        return { color: "bg-gray-400", label: status, animate: false };
    }
  };

  const config = getStatusConfig(status);

  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <div className={`h-2.5 w-2.5 rounded-full ${config.color}`} />
        {config.animate && (
          <div className={`absolute inset-0 h-2.5 w-2.5 rounded-full ${config.color} animate-ping opacity-75`} />
        )}
      </div>
      {showLabel && (
        <div className="flex items-center gap-1.5">
          <span className="text-sm font-medium text-gray-700">{config.label}</span>
          {agentType && (
            <span className="text-xs text-gray-500 capitalize">({agentType})</span>
          )}
          {duration !== undefined && status === "completed" && (
            <span className="text-xs text-gray-400">{duration.toFixed(1)}s</span>
          )}
        </div>
      )}
    </div>
  );
}
