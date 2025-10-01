import { Edge, Node, XYPosition } from "@xyflow/react";
import { DomainNode } from "../../types";
import { CIRCLE_SIZE } from "../../constants";

type NodeToRFOptions = {
  /** React Flow node type to use (defaults to "goal"). */
  defaultType?: Node["type"];
  /** Default position for nodes. */
  defaultPosition?: XYPosition;
  /** Circle size override (falls back to CIRCLE_SIZE). */
  size?: number;
  /** Force debug logging (in addition to non-production). */
  debug?: boolean;
};

/**
 * Adapt an array of `DomainNode` into React Flow `nodes` and `edges`.
 *
 * - Nodes are given a default type, size, and position unless overridden.
 * - Edges are validated (must have id, fromNode, toNode) and filtered so both
 *   endpoints exist in the input nodes.
 * - Duplicate edges (by `edgeId`) are deduplicated, last occurrence takes precedence.
 *
 * @param domainNodes - Source nodes from your domain model.
 * @param opts - Optional configuration for defaults and debug output.
 * @returns Object with `nodes` and `edges` arrays for React Flow.
 */
export function nodeToReactFlow(
  domainNodes: ReadonlyArray<DomainNode>,
  opts: NodeToRFOptions = {}
): { nodes: Node[]; edges: Edge[] } {
  const {
    defaultType = "goal",
    defaultPosition = { x: 0, y: 0 },
    size = CIRCLE_SIZE,
    debug = false,
  } = opts;

  const presentIds = new Set(domainNodes.map(({ nodeId }) => nodeId));

  /** React Flow nodes mapped from domain nodes. */
  const nodes: Node[] = domainNodes.map((n) => ({
    id: n.nodeId,
    type: defaultType,
    data: {
      nodeId: n.nodeId,
      title: n.title,
      status: n.status,
      kind: n.kind,
      parent: n.parent ?? null,
      smarter: n.smarter,
    },
    position: defaultPosition,
    width: size,
    height: size,
  }));

  /** Deduplicated and validated React Flow edges. */
  const edges: Edge[] = Array.from(
    new Map(
      domainNodes
        .flatMap((n) => n.edges ?? [])
        .filter((e): e is { edgeId: string; fromNode: string; toNode: string } =>
          Boolean(e && e.edgeId && e.fromNode && e.toNode)
        )
        .filter((e) => presentIds.has(e.fromNode) && presentIds.has(e.toNode))
        .map((e) => [
          e.edgeId,
          { id: e.edgeId, source: e.fromNode, target: e.toNode } as Edge,
        ])
    ).values()
  );

  if (debug || process.env.NODE_ENV !== "production") {
    console.debug("[adapt]", {
      nodes: nodes.length,
      rawEdges: domainNodes.reduce((sum, n) => sum + (n.edges?.length ?? 0), 0),
      keptEdges: edges.length,
    });
  }

  return { nodes, edges };
}