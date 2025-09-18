from __future__ import annotations

from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import TypeAdapter
from src.schemas.api_graph import BulkNodesRequest, BulkEdgesRequest, BulkWriteResponse
from src.schemas.graph import Graph
from src.schemas.node import NodeUnion
from src.schemas.edge import EdgeUnion
from src.services.graph_store import GraphStore

router = APIRouter(prefix="/graphs", tags=["graphs"])
_store = GraphStore()

_NODE_LIST = TypeAdapter(list[NodeUnion])  # reuse adapters (pydantic v2 best practice)
_EDGE_LIST = TypeAdapter(list[EdgeUnion])

def _nid(n: Any) -> Optional[str]:
    v = getattr(n, "node_id", None) or getattr(n, "nodeId", None)
    if v is None and isinstance(n, dict):
        v = n.get("nodeId") or n.get("node_id")
    return str(v) if v is not None else None

def _children(n: Any) -> list[Any]:
    ch = getattr(n, "nodes", None)
    if ch is None and isinstance(n, dict):
        ch = n.get("nodes")
    return ch if isinstance(ch, list) else []

def _find_node(container: list[Any], node_id: str) -> Optional[Any]:
    for n in container:
        if _nid(n) == node_id:
            return n
        ch = _children(n)
        hit = _find_node(ch, node_id) if ch else None
        if hit is not None:
            return hit
    return None

def _upsert_node(graph: Graph, node: Any) -> None:
    # Prefer aggregate method if you added it; fall back to local logic
    if hasattr(graph, "upsert_node"):
        graph.upsert_node(node)  # type: ignore[attr-defined]
        return

    # Fallback (replace-in-place or insert under parent or as root)
    def _parent(n: Any) -> Optional[str]:
        v = getattr(n, "parent", None)
        if v is None and isinstance(n, dict):
            v = n.get("parent")
        return str(v) if v is not None else None

    target = _nid(node)
    if target is None:
        raise ValueError("nodeId is required")

    def _replace(container: list[Any]) -> bool:
        for i, cur in enumerate(container):
            if _nid(cur) == target:
                container[i] = node
                return True
            ch = _children(cur)
            if ch and _replace(ch):
                return True
        return False

    roots = graph.nodes
    if _replace(roots):
        return

    pid = _parent(node)
    if pid is not None:
        host = _find_node(roots, pid)
        if host is None:
            raise ValueError(f"Parent node '{pid}' not found")
        ch = _children(host)
        if not isinstance(ch, list):
            setattr(host, "nodes", [])
            ch = getattr(host, "nodes")
        ch.append(node)
        return

    roots.append(node)

def _eid(e: Any) -> Optional[str]:
    v = getattr(e, "edge_id", None) or getattr(e, "edgeId", None)
    if v is None and isinstance(e, dict):
        v = e.get("edgeId") or e.get("edge_id")
    return str(v) if v is not None else None

def _from_to(e: Any) -> tuple[Optional[str], Optional[str]]:
    u = getattr(e, "from_node", None) or getattr(e, "fromNode", None)
    v = getattr(e, "to_node", None) or getattr(e, "toNode", None)
    if isinstance(e, dict):
        u = u or e.get("fromNode") or e.get("from_node")
        v = v or e.get("toNode") or e.get("to_node")
    return (str(u) if u is not None else None, str(v) if v is not None else None)

def _edges_of(n: Any) -> list[Any]:
    ch = getattr(n, "edges", None)
    if ch is None and isinstance(n, dict):
        ch = n.get("edges")
    return ch if isinstance(ch, list) else []

def _upsert_edge(graph: Graph, edge: Any) -> None:
    # Strategy: if graph has a root `edges` list, prefer it.
    if hasattr(graph, "edges"):
        root_edges = getattr(graph, "edges")
        if isinstance(root_edges, list):
            eid = _eid(edge)
            for i, e in enumerate(root_edges):
                if _eid(e) == eid and eid is not None:
                    root_edges[i] = edge
                    return
            root_edges.append(edge)
            return

    # Else attach to the source node’s `edges`
    (src, _dst) = _from_to(edge)
    if src is None:
        raise ValueError("edge.fromNode is required")
    host = _find_node(graph.nodes, src)
    if host is None:
        # allow dangling; validator endpoint will flag unknown-node
        return
    host_edges = _edges_of(host)
    if not isinstance(host_edges, list):
        setattr(host, "edges", [])
        host_edges = getattr(host, "edges")
    eid = _eid(edge)
    for i, e in enumerate(host_edges):
        if _eid(e) == eid and eid is not None:
            host_edges[i] = edge
            return
    host_edges.append(edge)

@router.post("/{graph_id}/nodes:bulk", response_model=BulkWriteResponse, summary="Bulk upsert nodes")
def bulk_nodes(graph_id: str, payload: BulkNodesRequest) -> BulkWriteResponse:
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

    nodes = _NODE_LIST.validate_python(payload.nodes)  # strict union validation
    for n in nodes:
        _upsert_node(g, n)
    _store.save(g)
    return BulkWriteResponse(nodes_upserted=len(nodes), edges_upserted=0)

@router.post("/{graph_id}/edges:bulk", response_model=BulkWriteResponse, summary="Bulk upsert edges")
def bulk_edges(graph_id: str, payload: BulkEdgesRequest) -> BulkWriteResponse:
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

    edges = _EDGE_LIST.validate_python(payload.edges)  # strict union validation
    for e in edges:
        _upsert_edge(g, e)
    _store.save(g)
    return BulkWriteResponse(nodes_upserted=0, edges_upserted=len(edges))