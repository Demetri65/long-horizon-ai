"use client";

import { UIMessage } from "ai";
import ELK, { ElkExtendedEdge, ElkNode } from "elkjs/lib/elk.bundled.js";
import React, { useCallback, useLayoutEffect, useEffect, useRef, useState } from "react";
import {
  ReactFlow,
  ReactFlowProvider,
  addEdge,
  Panel,
  useNodesState,
  useEdgesState,
  useReactFlow,
  Handle,
  type Node,
  type Edge,
  type Connection,
  type NodeProps,
  Position,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

// --- ELK setup (keep options minimal, configurable) ---
const elk = new ELK();
const elkOptions = {
  "elk.algorithm": "layered",
  "elk.layered.spacing.nodeNodeBetweenLayers": "100",
  "elk.spacing.nodeNode": "80",
} as Record<string, string>;

function useFitToCircle() {
  const ref = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const content = ref.current;
    const parent = content?.parentElement as HTMLElement | null;
    if (!content || !parent) return;

    let raf = 0;
    const measure = () => {
      // Available box inside the circle (minus padding already on the parent)
      const availW = parent.clientWidth;
      const availH = parent.clientHeight;

      // Measure unscaled content size
      const { scrollWidth, scrollHeight } = content;

      // Compute downscale factor if content would overflow
      const s = Math.min(1, availW / Math.max(1, scrollWidth), availH / Math.max(1, scrollHeight));

      // Avoid layout thrash; set only when the delta is meaningful
      if (Number.isFinite(s) && Math.abs(s - scale) > 0.02) {
        setScale(s);
      }
    };

    const ro = new ResizeObserver(() => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(measure);
    });

    ro.observe(parent);
    ro.observe(content);

    // Also run once initially
    raf = requestAnimationFrame(measure);

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
    };
  }, [scale]);

  return { ref, scale };
}

// size we want for our circular node (used by DOM and as ELK fallback)
const CIRCLE_SIZE = 120;     // NEW

// --- Domain types (for clarity only; your incoming data can still be `any`) ---
type DomainEdge = { edgeId: string; fromNode: string; toNode: string; label?: string };
type DomainNode = {
  kind?: string;
  nodeId: string;
  title?: string;
  status?: string;
  parent?: string | null;    // NEW (you stream this)
  smarter?: unknown;         // NEW (you stream this)
  edges?: DomainEdge[];
};
type DomainGraph = { nodes: DomainNode[] } | DomainNode[] | undefined | null;

export type GoalNodeProps = NodeProps & {
  data: DomainNode;           // NEW: use our domain node type
};

// --- Custom circular node (transparent bg + border) ---
// Best practice: a small, memoized component that reads positions from props.
const GoalNode = React.memo(
  (props: GoalNodeProps) => {
    const { data, sourcePosition, targetPosition, selected } = props;

    // auto-fit scaler
    const { ref, scale } = useFitToCircle();

    return (
      <div
        // The circle container — fixed size for ELK, flex-center for content
        style={{
          width: CIRCLE_SIZE,
          height: CIRCLE_SIZE,
          borderRadius: "50%",
          background: "transparent",
          border: "2px solid orange-600",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxSizing: "border-box",
          padding: 8,
          // Optional: enable container query units for the text (see below)
          containerType: "size",
        }}
        className="border-4 border-solid border-green-600 p-4"
      >
        {/* Scaler wrapper: we scale *this* block when content would overflow */}
        <div
          ref={ref}
          style={{
            transform: `scale(${scale})`,
            transformOrigin: "center center",
            // Let content define its own size naturally; we just scale it
            display: "block",
            maxWidth: "100%",
            maxHeight: "100%",
            overflow: "hidden",
          }}
        >
          {/* Actual text content */}
          <div
            style={{
              // Fluid base font; container-query units scale with circle size
              // 10cqw ≈ 10% of container width; for 120px circle ≈ 12px
              fontSize: "clamp(10px, 10cqw, 14px)",
              lineHeight: 1.2,
              textAlign: "center",
              wordBreak: "break-word",
              overflowWrap: "anywhere",
              // Avoid adding fixed heights; let auto-fit hook shrink if needed
            }}
          >
            <div style={{ fontWeight: 600 }}>{data?.title ?? "(untitled)"}</div>
            {data?.status && <div style={{ opacity: 0.9 }}>{data.status}</div>}
            <div style={{ opacity: 0.6 }}>{data?.nodeId}</div>
            {data?.kind && <div style={{ opacity: 0.6 }}>kind: {data.kind}</div>}
            {data?.parent && <div style={{ opacity: 0.6 }}>parent: {data.parent}</div>}
          </div>
        </div>

        {/* Handles honor the layout's direction via NodeProps */}
        <Handle type="target" position={targetPosition ?? Position.Top} />
        <Handle type="source" position={sourcePosition ?? Position.Bottom} />
      </div>
    );
  }
);

// Register node types (best practice: stable reference)
const nodeTypes = { goal: GoalNode };   // NEW

// --- Helper: normalize input shape to a flat array of DomainNode ---
function normalizeGraph(graph: DomainGraph): DomainNode[] {
  if (!graph) return [];
  return Array.isArray(graph) ? graph : Array.isArray((graph as any).nodes) ? (graph as any).nodes : [];
}

// --- Helper: adapt your domain nodes/edges to ReactFlow nodes/edges ---
function adaptDomainToReactFlow(domainNodes: DomainNode[]): { nodes: Node[]; edges: Edge[] } {
  const presentIds = new Set(domainNodes.map((n) => n.nodeId));

  // CHANGED: provide type: 'goal', pass all fields via data, and set width/height
  const nodes: Node[] = domainNodes.map((n) => ({
    id: n.nodeId,
    type: "goal", // use our custom circle node for all
    data: {
      nodeId: n.nodeId,
      title: n.title,
      status: n.status,
      kind: n.kind,
      parent: n.parent ?? null,
      smarter: n.smarter,
    },
    position: { x: 0, y: 0 }, // ELK will layout
    // These help ELK before the DOM is measured
    width: CIRCLE_SIZE,
    height: CIRCLE_SIZE,
  }));

  // collect raw edges across all nodes
  const raw: Edge[] = [];
  for (const n of domainNodes) {
    for (const e of n.edges ?? []) {
      if (!e.edgeId || !e.fromNode || !e.toNode) continue;
      raw.push({ id: e.edgeId, source: e.fromNode, target: e.toNode });
    }
  }

  // keep only those whose endpoints exist now
  const filtered = raw.filter((e) => presentIds.has(e.source) && presentIds.has(e.target));

  // de-dupe by id (last wins)
  const byId = new Map<string, Edge>();
  for (const e of filtered) byId.set(e.id, e);
  const edges = Array.from(byId.values());

  if (process.env.NODE_ENV !== "production") {
    console.debug(`[adapt] nodes=${nodes.length} rawEdges=${raw.length} keptEdges=${edges.length}`);
  }

  return { nodes, edges };
}

// --- ELK layout (based on React Flow's example) ---
async function getLayoutedElements(
  rfNodes: Node[],
  rfEdges: Edge[],
  options: Record<string, string> = {}
) {
  const isHorizontal = options["elk.direction"] === "RIGHT";

  const elkGraph = {
    id: "root",
    layoutOptions: { ...elkOptions, ...options },
    children: rfNodes.map((n) => ({
      id: n.id,
      // fallback to our circle size if not measured
      width: (n as any).width ?? CIRCLE_SIZE,
      height: (n as any).height ?? CIRCLE_SIZE,
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
}

export type GraphSectionProps = {
  streamStatus?: string;
  graph: any;          // can be { nodes: DomainNode[] } or DomainNode[]
  messages?: UIMessage[]; // retained to avoid broader changes; unused here
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
        await getLayoutedElements(nextNodes, nextEdges, opts);

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
    const { nodes: rfNodes, edges: rfEdges } = adaptDomainToReactFlow(domain);
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