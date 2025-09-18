"use client";

import { Graph } from "@/lib/api/client";

export type GraphSectionProps = {
  graph: Graph | null;
};

export const GraphSection = ({ graph }: GraphSectionProps) => {
    if (!graph) {
    return (
      <div className="w-full max-w-5xl p-6 text-zinc-300">
        No graph yet — send a prompt to start.
      </div>
    );
  }
  const goals = (graph.nodes ?? []).filter((n: any) => n.kind === "goal");

  return (
    <div className="w-full h-[50%] p-4 bg-slate-600 rounded-lg">
      <h2 className="text-lg font-semibold mb-3">High-level Goals (chronological)</h2>
      <ol className="list-decimal pl-6 space-y-1">
        {goals.map((g: any) => (
          <li key={g.nodeId}>{g.title}</li>
        ))}
      </ol>
    </div>
  );
}