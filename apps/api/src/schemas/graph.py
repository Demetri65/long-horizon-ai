from typing import Dict, Iterable, Iterator, List, Optional, Set
from pydantic import Field, model_validator
from src.config import ModelBase
from .node import GoalNode, NodeUnion
from .edge import DependencyEdge, EdgeBase, EdgeUnion, ContributesToEdge

class Graph(ModelBase):
    graph_id: str
    nodes: list[NodeUnion] = Field(default_factory=list)
    edges: list[EdgeUnion] = Field(default_factory=list)

    @staticmethod
    def _iter_metrics(node) -> Iterable:
        """Return Metric objects from a node."""
        s = getattr(node, "smarter", None)
        if s is None:
            return []
        meas = getattr(s, "measurable", None)
        if meas is None:
            return []
        if isinstance(meas, list): 
            return meas
        return getattr(meas, "metrics", []) or [] 

    @model_validator(mode="after")
    def check_invariants(self) -> "Graph":
        ids: Set[str] = set()
        metric_map: Dict[str, Set[str]] = {}

        def walk(n: NodeUnion):
            # Unique node ids
            if n.node_id in ids:
                raise ValueError(f"Duplicate node_id: {n.node_id}")
            ids.add(n.node_id)

            # Collect per-goal metric ids (null-safe)
            metrics = {m.metric_id for m in self._iter_metrics(n)}
            if getattr(n, "kind", None) == "goal" and metrics:
                metric_map[n.node_id] = metrics

            # Prefer n.nodes; fall back to n.children; walk once
            children = getattr(n, "nodes", None)
            if children is None:
                children = getattr(n, "children", None)
            for child in (children or []):
                walk(child)

        for n in (self.nodes or []):
            walk(n)

        # Edge sanity checks
        for e in (self.edges or []):
            if e.from_node not in ids or e.to_node not in ids:
                raise ValueError(f"Edge {e.edge_id} references unknown node(s)")

            if getattr(e, "kind", None) == "contributes_to":
                ce: ContributesToEdge = e  # type: ignore
                target_metrics = metric_map.get(ce.to_node, set())
                if target_metrics and not set(ce.metric_ids).issubset(target_metrics):
                    missing = sorted(set(ce.metric_ids) - target_metrics)
                    raise ValueError(
                        f"Edge {e.edge_id} has unknown metricIds on target {ce.to_node}: {missing}"
                    )
        return self

    
    def _iter_nodes_preorder(self) -> Iterator[NodeUnion]:
        """Non-recursive pre-order traversal of nested nodes (Graph.nodes[*].nodes[*]...)."""
        stack = list(self.nodes)[::-1]
        while stack:
            n = stack.pop()
            yield n
            if getattr(n, "nodes", None):
                stack.extend(list(n.nodes)[::-1])

    def flatten_nodes(self) -> list[NodeUnion]:
        """Return a flat list of every node in the nested graph structure."""
        return list(self._iter_nodes_preorder())
    
    def upsert_node(self, node: NodeUnion) -> "Graph":
        """
        Upsert `node` into this Graph.
        - If a node with the same node_id exists anywhere, replace it in-place.
        - Else, if `node.parent` is set, insert as a child of that parent.
        - Else, append as a new root node.
        Returns self for chaining.
        """
        def _nid(node: NodeUnion) -> Optional[str]:
            # accept Pydantic or dict-shaped nodes (snake/camel)
            v = getattr(node, "node_id", None) or getattr(node, "nodeId", None)
            if v is None and isinstance(node, dict):
                v = node.get("nodeId") or node.get("node_id")
            return str(v) if v is not None else None

        def _parent(node: NodeUnion) -> Optional[str]:
            v = getattr(node, "parent", None)
            if v is None and isinstance(node, dict):
                v = node.get("parent")
            return str(v) if v is not None else None

        def _children(node: NodeUnion) -> List[NodeUnion]:
            ch = getattr(node, "nodes", None)
            if ch is None and isinstance(node, dict):
                ch = node.get("nodes")
            return ch if isinstance(ch, list) else []

        target_id = _nid(node)
        if target_id is None:
            raise ValueError("node.nodeId is required for upsert_node")

        def _replace_in(container: List[NodeUnion]) -> bool:
            for i, cur in enumerate(container):
                if _nid(cur) == target_id:
                    container[i] = node
                    return True
                # recurse into children
                ch = _children(cur)
                if ch and _replace_in(ch):
                    return True
            return False

        roots = self.nodes
        if _replace_in(roots):
            return self

        # 2) Insert under parent if provided
        parent_id = _parent(node)
        if parent_id is not None:
            def _find(container: List[NodeUnion], pid: str) -> Optional[NodeUnion]:
                for cur in container:
                    if _nid(cur) == pid:
                        return cur
                    ch = _children(cur)
                    if ch:
                        hit = _find(ch, pid)
                        if hit is not None:
                            return hit
                return None

            host = _find(roots, parent_id)
            if host is None:
                raise ValueError(f"Parent node '{parent_id}' not found for upsert")

            host_children = _children(host)
            if not isinstance(host_children, list):
                try:
                    setattr(host, "nodes", [])
                    host_children = getattr(host, "nodes")
                except Exception:
                    if isinstance(host, dict):
                        host["nodes"] = []
                        host_children = host["nodes"]
                    else:
                        raise
            host_children.append(node)
            return self
        roots.append(node)
        return self
    