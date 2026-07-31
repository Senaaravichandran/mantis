"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { formatDateTime } from "@/lib/utils";

interface Thought {
  agent: string;
  thought: string;
  timestamp?: string;
  action?: string;
  result?: string;
}

interface Props {
  thoughts: Thought[];
  isLive?: boolean;
}

const AGENT_COLORS: Record<string, string> = {
  sentinel: "bg-blue-100 text-blue-800",
  analyst: "bg-purple-100 text-purple-800",
  planner: "bg-amber-100 text-amber-800",
  reporter: "bg-green-100 text-green-800",
  contractor: "bg-orange-100 text-orange-800",
  regulator: "bg-red-100 text-red-800",
};

export function AgentThoughtChain({ thoughts, isLive = false }: Props) {
  const [expandedIdx, setExpandedIdx] = useState<Set<number>>(new Set());

  const toggleExpand = (idx: number) => {
    const next = new Set(expandedIdx);
    if (next.has(idx)) next.delete(idx);
    else next.add(idx);
    setExpandedIdx(next);
  };

  if (!thoughts || thoughts.length === 0) {
    return (
      <div className="text-sm text-gray-500 py-4">
        {isLive ? "Waiting for agent reasoning..." : "No reasoning chain available."}
      </div>
    );
  }

  return (
    <div className="space-y-0">
      {thoughts.map((thought, i) => {
        const isExpanded = expandedIdx.has(i);
        const isLast = i === thoughts.length - 1;

        return (
          <div key={i} className="relative pl-8">
            {/* Vertical line */}
            {!isLast && (
              <div className="absolute left-[11px] top-6 bottom-0 w-0.5 bg-gray-200" />
            )}

            {/* Dot */}
            <div
              className={`absolute left-1 top-1.5 h-4 w-4 rounded-full border-2 border-white ${
                isLast && isLive ? "bg-mantis-600 animate-pulse" : "bg-mantis-600"
              }`}
            />

            <div className="pb-4">
              <button
                onClick={() => toggleExpand(i)}
                className="w-full text-left rounded-lg border p-3 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-2 mb-1">
                  <Badge className={AGENT_COLORS[thought.agent] || "bg-gray-100 text-gray-800"}>
                    {thought.agent}
                  </Badge>
                  {thought.action && (
                    <span className="text-xs text-gray-500">{thought.action}</span>
                  )}
                  {thought.timestamp && (
                    <span className="text-xs text-gray-400 ml-auto">
                      {formatDateTime(thought.timestamp)}
                    </span>
                  )}
                </div>
                <p className={`text-sm text-gray-700 ${isExpanded ? "" : "line-clamp-2"}`}>
                  {thought.thought}
                </p>
                {thought.result && isExpanded && (
                  <div className="mt-2 rounded bg-gray-50 p-2">
                    <p className="text-xs font-medium text-gray-500 mb-1">Result:</p>
                    <p className="text-xs text-gray-600 whitespace-pre-wrap">{thought.result}</p>
                  </div>
                )}
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
