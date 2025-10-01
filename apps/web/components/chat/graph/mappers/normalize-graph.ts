import { DomainGraph, DomainNode } from "../../types";

export const normalizeGraph = (graph: DomainGraph): DomainNode[] => {
  if (!graph) return [];
  return Array.isArray(graph) ? graph : Array.isArray((graph as any).nodes) ? (graph as any).nodes : [];
}