"use client";

import { UIMessage } from "ai";
import React, { useCallback, useLayoutEffect} from "react";
import { GoalNode } from "@/components/chat/graph/nodes/goal-node";
import { normalizeGraph } from "@/components/chat/graph/mappers/normalize-graph";
import { nodeToReactFlow } from "@/components/chat/graph/mappers/node-to-react-flow";
import { useElkLayout } from "@/components/chat/graph/hooks/use-elk-layout";
import { elkOptions } from "@/components/chat/constants";
import {
  ReactFlow,
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  useReactFlow,
  type Node,
  type Edge,
  type Connection,
} from "@xyflow/react";

const nodeTypes = { goal: GoalNode };

export type GraphSectionProps = {
  streamStatus?: string;
  graph: any;          
  messages?: UIMessage[]; 
};

// --- Internal: content that binds the graph prop to RF + ELK ---
const GraphContent = ({ graph, streamStatus }: GraphSectionProps) => {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const { fitView } = useReactFlow();

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Stable layout function that uses provided next elements
  const onLayout = useCallback(
    async ({
      direction,
      nextNodes = [],
      nextEdges = [],
    }: { direction: "RIGHT" | "DOWN"; nextNodes?: Node[]; nextEdges?: Edge[] }) => {
      const opts = { "elk.direction": direction, ...elkOptions };
      const { nodes: laidOutNodes, edges: laidOutEdges } =
        await useElkLayout(nextNodes, nextEdges, opts);

      setNodes(laidOutNodes);
      setEdges(laidOutEdges);
      fitView();
    },
    [setNodes, setEdges, fitView]
  );

  // Rebuild + layout whenever the domain graph changes (incremental-friendly)
  useLayoutEffect(() => {
    const domain = normalizeGraph(graph);
    if (!domain.length) {
      setNodes([]);
      setEdges([]);
      return;
    }
    const { nodes: rfNodes, edges: rfEdges } = nodeToReactFlow(domain);
    // Do layout immediately with the newly adapted elements
    onLayout({ direction: "RIGHT", nextNodes: rfNodes, nextEdges: rfEdges });
  }, [graph, onLayout, setNodes, setEdges]);

  return (
    // CHANGED: ensure non-zero height so ELK/ReactFlow can lay out properly
    <div className="w-full min-h-[420px] p-4 bg-slate-600 rounded-lg">
      <h2 className="text-lg font-semibold">High-level Goals (chronological)</h2>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}            // NEW: register custom node
        onConnect={onConnect}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodesDraggable={false}
        panOnDrag={false}
        elementsSelectable={streamStatus === "streaming" ? false : true}
        zoomOnScroll={false}
        panOnScroll={false}
        proOptions={{ hideAttribution: true }}
        fitView
      >
      </ReactFlow>
    </div>
  );
};

export const GraphSection = (props: GraphSectionProps) => {
  return (
    <ReactFlowProvider>
      <GraphContent {...props} />
    </ReactFlowProvider>
  );
};