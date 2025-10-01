import { Edge, Node, Position } from "@xyflow/react";
import { CIRCLE_SIZE, elk, elkOptions } from "../../constants";
import { ElkExtendedEdge, ElkNode } from "elkjs/lib/elk.bundled";

export const useElkLayout = async (
  rfNodes: Node[],
  rfEdges: Edge[],
  options: Record<string, string> = {}
) => {
  const isHorizontal = options["elk.direction"] === "RIGHT";

  const elkGraph = {
    id: "root",
    layoutOptions: { ...elkOptions, ...options },
    children: rfNodes.map((n) => ({
      id: n.id,
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