from __future__ import annotations

from typing import Optional, Set, List, Dict, Any, Callable
from fastapi import APIRouter, HTTPException, Query
from src.schemas.api_graph import (
    ValidateIssue, ValidateResponse,
    TraverseResponse, TopoResponse,
    CriticalPathResponse, CriticalPathNode, RollupResponse,
)
from src.schemas.enums import EdgeKind
from src.services.graph_store import GraphStore
from src.services.graph_index import GraphIndex
from src.services.graph_ops import GraphOps

router = APIRouter(prefix="/graphs", tags=["graphs"])
_store = GraphStore()

def _parse_edge_kinds(csv: Optional[str]) -> Set[str]:
    if not csv:
        return set()
    kinds = {k.strip() for k in csv.split(",") if k.strip()}
    enum_kinds = {k.value for k in EdgeKind}
    unknown = kinds - enum_kinds
    if unknown:
        raise HTTPException(422, f"Unknown edgeKinds: {sorted(list(unknown))}")
    return kinds

@router.get("/{graph_id}/validate", response_model=ValidateResponse, summary="Validate graph invariants")
def validate_graph(graph_id: str) -> ValidateResponse:
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

    idx = GraphIndex.from_graph(g)
    ops = GraphOps(idx)

    issues: List[ValidateIssue] = []

    for i in ops.check_node_id_duplicates():
        issues.append(ValidateIssue(code="duplicate-node", message=i["message"], path=i.get("path")))
    for i in ops.check_edge_node_refs():
        issues.append(ValidateIssue(code="unknown-edge-node", message=i["message"], path=i.get("path")))
    for i in ops.check_contrib_metrics():
        issues.append(ValidateIssue(code="missing-contrib-metric", message=i["message"], path=i.get("path")))

    cycles = ops.detect_cycles(dep_kind=EdgeKind.dependency.value)
    if cycles:
        for cyc in cycles:
            issues.append(ValidateIssue(code="cycle-detected", message="Dependency cycle", path=[",".join(cyc)]))

    return ValidateResponse(ok=(len(issues) == 0), issues=issues)

@router.get("/{graph_id}/traverse", response_model=TraverseResponse, summary="BFS traversal over selected edge kinds")
def traverse_graph(
    graph_id: str,
    start: str = Query(..., description="Start nodeId"),
    edge_kinds: Optional[str] = Query(None, description="CSV of edge kinds (dependency,contributes_to,relates_to,validates)"),
    # Pydantic v2 uses `pattern` (regex was removed). See migration notes.
    direction: str = Query("out", pattern="^(in|out)$"),
    depth: Optional[int] = Query(None, ge=0),
) -> TraverseResponse:
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

    kinds = _parse_edge_kinds(edge_kinds) or {EdgeKind.dependency.value}
    idx = GraphIndex.from_graph(g)
    ops = GraphOps(idx)
    order = ops.bfs(start=start, kinds=kinds, direction=direction, depth=depth)
    return TraverseResponse(order=order, visited=len(order))

@router.get("/{graph_id}/topo", response_model=TopoResponse, summary="Topological order of dependency DAG")
def topo_order(graph_id: str) -> TopoResponse:
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

    idx = GraphIndex.from_graph(g)
    ops = GraphOps(idx)
    cycles = ops.detect_cycles(dep_kind=EdgeKind.dependency.value)
    if cycles:
        return TopoResponse(order=[], cycles=cycles)
    return TopoResponse(order=ops.topological_order(dep_kind=EdgeKind.dependency.value))

@router.get("/{graph_id}/critical-path", response_model=CriticalPathResponse, summary="Critical path over dependency edges")
def critical_path(graph_id: str) -> CriticalPathResponse:
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

    idx = GraphIndex.from_graph(g)
    ops = GraphOps(idx)

    # Call dynamically so static type checkers don't flag missing attribute
    func: Optional[Callable[[], Any]] = getattr(ops, "critical_path", None)
    if not callable(func):
        # Keep endpoint documented but return 501 until service method exists
        raise HTTPException(501, "critical_path not implemented in GraphOps")

    cp = func()  # expected to expose `.path` (iterable of nodes) and `.total_lag_hours`
    nodes_out: List[CriticalPathNode] = []

    for n in getattr(cp, "path", []):
        node_id: str = getattr(n, "node_id") or getattr(n, "nodeId")
        nodes_out.append(
            CriticalPathNode(
                nodeId=node_id,
                earliest_start=getattr(n, "earliest_start", None),
                latest_finish=getattr(n, "latest_finish", None),
            )
        )

    return CriticalPathResponse(
        path=nodes_out,
        total_lag_hours=getattr(cp, "total_lag_hours", None),
    )

@router.get("/{graph_id}/rollup", response_model=RollupResponse, summary="Roll up metrics to a goal")
def rollup(graph_id: str, goal: str = Query(..., description="Target goal nodeId")) -> RollupResponse:
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

    idx = GraphIndex.from_graph(g)
    ops = GraphOps(idx)

    # This endpoint returns a mapping metricId -> rolled value(s)
    func: Optional[Callable[..., Dict[str, Any]]] = getattr(ops, "rollup_metrics", None)
    if not callable(func):
        raise HTTPException(501, "rollup_metrics not implemented in GraphOps")

    metrics: Dict[str, Any] = func(target_goal=goal)
    if not isinstance(metrics, dict):
        raise HTTPException(500, "rollup_metrics must return a dict[str, Any]")

    return RollupResponse(metrics=metrics)