import { NodeProps } from "@xyflow/react";

export type DomainEdge = { edgeId: string; fromNode: string; toNode: string; label?: string };
export type DomainNode = {
  kind?: string;
  nodeId: string;
  title?: string;
  status?: string;
  parent?: string | null;    // NEW (you stream this)
  smarter?: unknown;         // NEW (you stream this)
  edges?: DomainEdge[];
};
export type DomainGraph = { nodes: DomainNode[] } | DomainNode[] | undefined | null;

export type GoalNodeProps = NodeProps & {
  data: DomainNode;   
};