from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Iterable

from src.schemas.graph import Graph
from src.schemas.node import NodeUnion
from src.schemas.edge import EdgeUnion

@dataclass(slots=True)
class GraphIndex:
    """
    A read-only, in-memory index for fast graph operations.
    It builds a directed graph index from a Graph schema, allowing efficient
    traversal and querying of nodes and edges.
    """
    id_to_node: Dict[str, NodeUnion] = field(default_factory=dict)
    children_of: Dict[str, List[str]] = field(default_factory=dict)
    parents_of: Dict[str, List[str]] = field(default_factory=dict)

    # Edges (directed, from -> to)
    out_edges_of: Dict[str, List[EdgeUnion]] = field(default_factory=dict)
    in_edges_of: Dict[str, List[EdgeUnion]] = field(default_factory=dict)

    # Metric catalog for rollups: nodeId -> set(metricIds) (typically goals)
    metrics_on: Dict[str, Set[str]] = field(default_factory=dict)

    @classmethod
    def from_graph(cls, g: Graph) -> "GraphIndex":
        """
        Build an index from a Graph. We consume BOTH:
          - g.nodes[*] recursively with their .nodes and .edges (outgoing)
          - g.edges at the root (if present)
        """
        index = cls()
        # 1) Flatten nodes and collect metrics
        for n in _iter_nodes_recursive(g.nodes):
            nid = n.node_id
            index.id_to_node[nid] = n
            # children/parents from nesting (not from edges)
            index.children_of.setdefault(nid, [])
            index.parents_of.setdefault(nid, [])
            for c in n.nodes:
                cid = c.node_id
                index.children_of[nid].append(cid)
                index.parents_of.setdefault(cid, []).append(nid)

            # measurable metrics on goals
            if getattr(n, "kind", None) == "goal":
                # n.smarter.smarter.measurable -> list of Metric(model)
                metrics = getattr(n.smarter.smarter, "measurable", [])
                mids = {m.metric_id for m in metrics}
                if mids:
                    index.metrics_on[nid] = mids

            # outgoing edges stored on the node (if you keep them here)
            if getattr(n, "edges", None):
                for e in n.edges:
                    index._add_edge(e)

        # 2) Root-level edges (if you also store them there)
        for e in getattr(g, "edges", []) or []:
            index._add_edge(e)

        # Ensure every node id is present in edge maps
        for nid in index.id_to_node:
            index.out_edges_of.setdefault(nid, [])
            index.in_edges_of.setdefault(nid, [])

        return index

    def _add_edge(self, e: EdgeUnion) -> None:
        """Add a directed edge to the adjacency maps."""
        self.out_edges_of.setdefault(e.from_node, []).append(e)
        self.in_edges_of.setdefault(e.to_node, []).append(e)

    # ---- Convenience API for algorithms ----

    def out_neighbors(self, node_id: str, kinds: Set[str] | None = None) -> List[str]:
        edges = self.out_edges_of.get(node_id, [])
        if kinds:
            return [e.to_node for e in edges if getattr(e, "kind", None) in kinds]
        return [e.to_node for e in edges]

    def in_neighbors(self, node_id: str, kinds: Set[str] | None = None) -> List[str]:
        edges = self.in_edges_of.get(node_id, [])
        if kinds:
            return [e.from_node for e in edges if getattr(e, "kind", None) in kinds]
        return [e.from_node for e in edges]

    def in_degree(self, kind: str | None = None) -> Dict[str, int]:
        """
        In-degree over an optional single edge kind (most common: 'dependency').
        If kind is None, count all incoming edges.
        """
        indeg: Dict[str, int] = {nid: 0 for nid in self.id_to_node}
        for nid, incoming in self.in_edges_of.items():
            if kind is None:
                indeg[nid] = len(incoming)
            else:
                indeg[nid] = sum(1 for e in incoming if getattr(e, "kind", None) == kind)
        return indeg


def _iter_nodes_recursive(nodes: Iterable[NodeUnion]):
    """Yield nodes in a pre-order traversal over the nested 'nodes' tree."""
    stack = list(nodes)[::-1]
    while stack:
        n = stack.pop()
        yield n
        # push children in reverse to visit left-to-right
        if getattr(n, "nodes", None):
            stack.extend(list(n.nodes)[::-1])