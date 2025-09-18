from __future__ import annotations

from collections import Counter, deque
from typing import List, Set, Dict, Tuple, Optional, Iterable, Any

from src.schemas.enums import EdgeKind
from src.services.graph_index import GraphIndex

class GraphOps:
    """
    Stateless algorithms over a GraphIndex.

      - BFS/DFS for exploration
      - Kahn's algorithm for topological sort (dependency DAGs)
      - Optional shortest/longest paths
    """

    def __init__(self, index: GraphIndex):
        self.idx = index

    def bfs(
        self,
        start: str,
        kinds: Set[str] | None = None,
        direction: str = "out",
        depth: int | None = None,
    ) -> List[str]:
        """
        Breadth-first traversal returning the visitation order.
        - direction: 'out' to follow outgoing edges, 'in' for incoming
        - kinds: restrict traversal to a subset of edge kinds (e.g., {'dependency'})
        - depth: limit traversal depth (0 => start only)
        Complexity: O(N+E) for explored subgraph.
        """
        if start not in self.idx.id_to_node:
            return []

        seen = {start}
        q = deque([(start, 0)])
        order: List[str] = []

        step = (
            (lambda n: self.idx.out_neighbors(n, kinds))
            if direction == "out" else
            (lambda n: self.idx.in_neighbors(n, kinds))
        )

        while q:
            node, d = q.popleft()
            order.append(node)
            if depth is not None and d >= depth:
                continue
            for nxt in step(node):
                if nxt not in seen:
                    seen.add(nxt)                    
                    q.append((nxt, d + 1))
        return order

    def topological_order(self, dep_kind: str = EdgeKind.dependency.value) -> List[str]:
        """
        Kahn's algorithm. Raises ValueError if cycles exist.
        Only considers edges where kind == dep_kind (default: 'dependency').
        """
        indeg = self.idx.in_degree(dep_kind)
        zero = [n for n, deg in indeg.items() if deg == 0]
        order: List[str] = []

        while zero:
            n = zero.pop()
            order.append(n)
            for m in self.idx.out_neighbors(n, {dep_kind}):
                indeg[m] -= 1
                if indeg[m] == 0:
                    zero.append(m)

        # any remaining incoming edges => cycle
        if any(deg > 0 for deg in indeg.values()):
            raise ValueError("dependency graph has cycles")

        return order

    def shortest_hops(
        self,
        src: str,
        dst: str,
        kinds: Set[str] | None = None,
        direction: str = "out",
    ) -> List[str]:
        """
        Unweighted shortest path (by hops) using BFS predecessor tracking.
        Returns [] if no path.
        """
        if src not in self.idx.id_to_node or dst not in self.idx.id_to_node:
            return []

        prev = {src: str(src)}
        q = deque([src])
        step = (
            (lambda n: self.idx.out_neighbors(n, kinds))
            if direction == "out" else
            (lambda n: self.idx.in_neighbors(n, kinds))
        )

        while q:
            u = q.popleft()
            if u == dst:
                break
            for v in step(u):
                if v not in prev:
                    prev[v] = u
                    q.append(v)

        if dst not in prev:
            return []

        # reconstruct
        cur, path = dst, []
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        return list(reversed(path))


    def detect_cycles(self, dep_kind: str = EdgeKind.dependency.value) -> List[List[str]]:
        """
        Find directed cycles over edges of kind `dep_kind` using Tarjan's SCC algorithm.
        Returns a list of cycles, each as a list of nodeIds (SCCs with size>1 or self-loop).
        Complexity: O(N+E). See Tarjan SCC / cycle↔SCC relationship. :contentReference[oaicite:1]{index=1}
        """
        # Build adjacency restricted to dep_kind
        nodes = list(self.idx.id_to_node.keys())
        adj: Dict[str, List[str]] = {n: list(self.idx.out_neighbors(n, {dep_kind})) for n in nodes}

        index = 0
        indices: Dict[str, int] = {}
        lowlink: Dict[str, int] = {}
        stack: List[str] = []
        onstack: Set[str] = set()
        sccs: List[List[str]] = []

        def strongconnect(v: str) -> None:
            nonlocal index
            indices[v] = index
            lowlink[v] = index
            index += 1
            stack.append(v)
            onstack.add(v)

            for w in adj.get(v, []):
                if w not in indices:
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif w in onstack:
                    lowlink[v] = min(lowlink[v], indices[w])

            # Root of an SCC?
            if lowlink[v] == indices[v]:
                comp: List[str] = []
                while True:
                    w = stack.pop()
                    onstack.remove(w)
                    comp.append(w)
                    if w == v:
                        break
                # SCC is a cycle if size>1 or (size==1 and self-loop exists)
                if len(comp) > 1:
                    sccs.append(comp)
                else:
                    u = comp[0]
                    if u in adj.get(u, []):
                        sccs.append([u])

        for v in nodes:
            if v not in indices:
                strongconnect(v)
        return sccs

    def check_contrib_metrics(self) -> List[Dict[str, Any]]:
        """
        Validate that every `contributes_to` edge references metricIds that actually
        exist on the *target* node's measurable metrics (per your schema rules).
        Returns a list of issue dicts: {'message': str, 'path': ['edges', edgeId] }.
        """
        issues: List[Dict[str, Any]] = []
        for (edge_id, kind, u, v, edge_obj) in self._iter_edges():
            if kind != EdgeKind.contributes_to.value:
                continue
            metric_ids = self._extract_metric_ids(edge_obj)
            if metric_ids is None:
                # cannot validate if edge does not carry metricIds (skip silently)
                continue
            target_metric_ids = self._metric_ids_on_node(v)
            missing = [m for m in metric_ids if m not in target_metric_ids]
            if missing:
                msg = f"Edge {edge_id or f'{u}->{v}'} references unknown metricIds on target {v}: {missing}"
                issues.append({"message": msg, "path": ["edges", str(edge_id) if edge_id else f"{u}->{v}"]})
        return issues

    def check_node_id_duplicates(self) -> List[Dict[str, Any]]:
        """
        Report duplicate nodeIds if the underlying index kept a raw list/multiset.
        If only a dict of nodes is available (id_to_node), duplicates cannot exist
        at index-time and we return [].
        """
        # Try to use any raw id collection preserved by the index
        raw_ids: Optional[List[str]] = None
        if hasattr(self.idx, "raw_node_ids"):
            raw_ids = list(getattr(self.idx, "raw_node_ids"))
        elif hasattr(self.idx, "nodes"):
            try:
                # handle Pydantic or dict-shaped nodes
                raw_ids = []
                for n in getattr(self.idx, "nodes"):
                    nid = getattr(n, "node_id", None) or getattr(n, "nodeId", None)
                    if nid is None and isinstance(n, dict):
                        nid = n.get("nodeId") or n.get("node_id")
                    if nid is not None:
                        raw_ids.append(str(nid))
            except Exception:
                raw_ids = None

        if not raw_ids:
           return []  # cannot prove duplicates from a dict-backed view

        
        dupes = [nid for nid, cnt in Counter(raw_ids).items() if cnt > 1]
        return [{"message": f"Duplicate node_id: {nid}", "path": ["nodes", nid]} for nid in dupes]

    def check_edge_node_refs(self) -> List[Dict[str, Any]]:
        """
        Verify that every edge's from_node/to_node exist among known nodeIds.
        Returns issue dicts: {'message': str, 'path': ['edges', edgeId]}.
        """
        issues: List[Dict[str, Any]] = []
        known = set(self.idx.id_to_node.keys())
        for (edge_id, kind, u, v, _edge) in self._iter_edges():
            missing = [x for x in (u, v) if x not in known]
            if missing:
                msg = f"Edge {edge_id or f'{u}->{v}'} references unknown node(s): {missing}"
                issues.append({"message": msg, "path": ["edges", str(edge_id) if edge_id else f"{u}->{v}"]})
        return issues

  # ----------------------------- private --------------------------------
    def _iter_edges(self) -> Iterable[Tuple[Optional[str], str, str, str, Any]]:
        """
        Yield (edge_id, kind, from, to, raw_edge_obj).
        - If GraphIndex exposes `edges` (list/iterable), we read from it.
        - Otherwise, we synthesize edges from neighbor lists per kind (edge_id=None).
        """
        # Prefer an explicit edge collection if available
        if hasattr(self.idx, "edges"):
            edges = getattr(self.idx, "edges")
            for e in edges:
                # Handle Pydantic objects or dicts
                edge_id = getattr(e, "edge_id", None) or getattr(e, "edgeId", None)
                kind = getattr(e, "kind", None) or (e.get("kind") if isinstance(e, dict) else None)
                u = getattr(e, "from_node", None) or getattr(e, "fromNode", None)
                v = getattr(e, "to_node", None) or getattr(e, "toNode", None)
                if isinstance(e, dict):
                    u = u or e.get("fromNode") or e.get("from_node")
                    v = v or e.get("toNode") or e.get("to_node")
                    edge_id = edge_id or e.get("edgeId") or e.get("edge_id")
                if kind and u and v:
                    yield (edge_id, kind, str(u), str(v), e)
            return

      # Fallback: synthesize edges from neighbor lists (no edge_id available)
      # This allows referential checks; metric validation may be skipped.
        all_kinds = {k.value for k in EdgeKind}
        for kind in all_kinds:
            for u in self.idx.id_to_node.keys():
                for v in self.idx.out_neighbors(u, {kind}):
                    yield (None, kind, u, v, None)

    def _metric_ids_on_node(self, node_id: str) -> Set[str]:
        """
        Extract measurable.metricIds for a target node (typically a 'goal').
        Supports Pydantic objects or dicts and both snake/camel case.
        """
        node = self.idx.id_to_node.get(node_id)
        if node is None:
            return set()
        # Try attribute forms
        payload = getattr(node, "smarter", None)
        # nested 'smarter.smarter' vs flat
        inner = getattr(payload, "smarter", None) if payload is not None else None
        measurable = None
        if inner is not None:
            measurable = getattr(inner, "measurable", None)
        elif payload is not None:
            measurable = getattr(payload, "measurable", None)
        # try dict forms
        if measurable is None:
            if isinstance(node, dict):
                payload = node.get("smarter") or {}
                inner = payload.get("smarter") if isinstance(payload, dict) else None
                if inner and isinstance(inner, dict):
                    measurable = inner.get("measurable")
                else:
                    measurable = payload.get("measurable")
        if not measurable:
            return set()
        ids: Set[str] = set()
        for m in measurable:
            mid = getattr(m, "metric_id", None) or getattr(m, "metricId", None)
            if mid is None and isinstance(m, dict):
                mid = m.get("metricId") or m.get("metric_id")
            if mid is not None:
                ids.add(str(mid))
        return ids

    def _extract_metric_ids(self, edge_obj: Any) -> Optional[List[str]]:
        """
        Robustly read metricIds from a contributes_to edge object (if available).
        Returns None if not present or if working from synthesized edges.
        """
        if edge_obj is None:
            return None
        mids = getattr(edge_obj, "metric_ids", None) or getattr(edge_obj, "metricIds", None)
        if mids is None and isinstance(edge_obj, dict):
            mids = edge_obj.get("metricIds") or edge_obj.get("metric_ids")
        if not mids:
            return None
        return [str(x) for x in mids]