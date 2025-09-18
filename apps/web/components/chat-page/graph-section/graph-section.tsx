"use client";

import { Graph } from "@/lib/api/client";
import { RawNode } from "@/lib/createNodeStreamParser";
import { UIMessage } from "ai";
import ELK, { ElkExtendedEdge, ElkNode } from 'elkjs/lib/elk.bundled.js';
import React, { useCallback, useLayoutEffect } from 'react';
import {
  Background,
  ReactFlow,
  ReactFlowProvider,
  addEdge,
  Panel,
  useNodesState,
  useEdgesState,
  useReactFlow,
  type Node,
  type Edge,
  type Connection,
  Position,
} from '@xyflow/react';

import '@xyflow/react/dist/style.css';
import { initialEdges, initialNodes } from "./temp-nodes";

const elk = new ELK();

const elkOptions = {
  'elk.algorithm': 'layered',
  'elk.layered.spacing.nodeNodeBetweenLayers': '100',
  'elk.spacing.nodeNode': '80',
};

const graph = {
  id: "root",
  layoutOptions: { 'elk.algorithm': 'layered' },
  children: [
    { id: "n1", width: 30, height: 30 },
    { id: "n2", width: 30, height: 30 },
    { id: "n3", width: 30, height: 30 }
  ],
  edges: [
    { id: "e1", sources: ["n1"], targets: ["n2"] },
    { id: "e2", sources: ["n1"], targets: ["n3"] }
  ]
}
elk.layout(graph)
  .then(console.log)
  .catch(console.error)

const getLayoutedElements = async (
  rfNodes: Node[],
  rfEdges: Edge[],
  options: Record<string, string> = {}
) => {
  const isHorizontal = options['elk.direction'] === 'RIGHT';

  const elkGraph = {
    id: 'root',
    layoutOptions: { ...elkOptions, ...options },
    children: rfNodes.map((n) => ({
      id: n.id,
      // ELK needs width/height to compute layout
      width: (n as any).width ?? 150,
      height: (n as any).height ?? 50,
    })),
    edges: rfEdges.map((e) => ({
      id: e.id,
      sources: [e.source],
      targets: [e.target],
    })),
  };

  const layouted = await elk.layout(elkGraph);

  const layoutedNodes: Node[] = (layouted.children as (ElkNode & { x: number; y: number })[]).map(
    (ln) => {
      const original = rfNodes.find((n) => n.id === ln.id)!;
      return {
        ...original,
        position: { x: ln.x, y: ln.y },
        targetPosition: isHorizontal ? Position.Left : Position.Top,
        sourcePosition: isHorizontal ? Position.Right : Position.Bottom,
      };
    }
  );

  const layoutedEdges: Edge[] = (layouted.edges as ElkExtendedEdge[]).map((le) => {
    const original = rfEdges.find((e) => e.id === le.id)!;
    return {
      ...original,
      source: le.sources[0],
      target: le.targets[0],
    };
  });

  return { nodes: layoutedNodes, edges: layoutedEdges };
};

export type GraphSectionProps = {
  graph: Graph | null;
  messages: UIMessage[];
};

const GraphContent = ({ graph, messages }: GraphSectionProps) => {
  if (!graph) {
    return (
      <div className="w-full max-w-5xl p-6 text-zinc-300">
        No graph yet — send a prompt to start.
      </div>
    );
  }
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const { fitView } = useReactFlow();

  const onConnect = useCallback(
  (params: Connection) => setEdges((eds) => addEdge(params, eds)),
  [setEdges]
);
  const onLayout = useCallback(
    ({ direction, useInitialNodes = false }) => {
      const opts = { 'elk.direction': direction, ...elkOptions };
      const ns = useInitialNodes ? initialNodes : nodes;
      const es = useInitialNodes ? initialEdges : edges;

      getLayoutedElements(ns, es, opts).then(
        ({ nodes: layoutedNodes, edges: layoutedEdges }) => {
          setNodes(layoutedNodes);
          setEdges(layoutedEdges);
          fitView();
        },
      );
    },
    [nodes, edges],
  );

  // Calculate the initial layout on mount.
  useLayoutEffect(() => {
    onLayout({ direction: 'RIGHT', useInitialNodes: true });
  }, []);


  return (
      <div className="w-full h-[50%] p-4 bg-slate-600 rounded-lg">
        <h2 className="text-lg font-semibold mb-3">High-level Goals (chronological)</h2>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onConnect={onConnect}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          draggable={false}
        >
          <Panel position="top-right">
            <button
              className="xy-theme__button"
            // onClick={() => onLayout({ direction: 'DOWN' })}
            >
              vertical layout
            </button>

            <button
              className="xy-theme__button"
            // onClick={() => onLayout({ direction: 'RIGHT' })}
            >
              horizontal layout
            </button>
          </Panel>
          {/* <Background /> */}
        </ReactFlow>
      </div>
  );
}

export const GraphSection = (props: GraphSectionProps) => {
  return (
    <ReactFlowProvider>
      <GraphContent {...props} />
    </ReactFlowProvider>
  );
}