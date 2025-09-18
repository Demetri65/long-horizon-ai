from __future__ import annotations

from typing import Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import TypeAdapter
from src.schemas.edge import EdgeUnion
from src.schemas.graph import Graph
from src.services.graph_store import GraphStore

router = APIRouter(prefix="/graphs", tags=["edges"])
_store = GraphStore()
_EDGE = TypeAdapter(EdgeUnion)

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

def _children(n: Any) -> list[Any]:
    ch = getattr(n, "nodes", None)
    if ch is None and isinstance(n, dict):
        ch = n.get("nodes")
    return ch if isinstance(ch, list) else []

def _find_node(container: list[Any], node_id: str) -> Optional[Any]:
    for n in container:
        nid = getattr(n, "node_id", None) or getattr(n, "nodeId", None) or (n.get("nodeId") if isinstance(n, dict) else None) or (n.get("node_id") if isinstance(n, dict) else None)
        if nid == node_id:
            return n
        ch = _children(n)
        hit = _find_node(ch, node_id) if ch else None
        if hit is not None:
            return hit
    return None

def _edges_of(n: Any) -> list[Any]:
    ch = getattr(n, "edges", None)
    if ch is None and isinstance(n, dict):
        ch = n.get("edges")
    return ch if isinstance(ch, list) else []

@router.post("/{graph_id}/edges", response_model=Graph, summary="Upsert a single edge, return full graph")
def upsert_edge(graph_id: str, edge: dict) -> Graph:
    edge_obj = _EDGE.validate_python(edge)
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

    # prefer root edges if exist; else attach to source node
    if hasattr(g, "edges") and isinstance(g.edges, list):  # type: ignore[attr-defined]
        eid = _eid(edge_obj)
        for i, e in enumerate(g.edges):  # type: ignore[attr-defined]
            if _eid(e) == eid and eid is not None:
                g.edges[i] = edge_obj  # type: ignore[attr-defined]
                _store.save(g)
                return g
        g.edges.append(edge_obj)        # type: ignore[attr-defined]
        _store.save(g)
        return g

    (src, _dst) = _from_to(edge_obj)
    if src is None:
        raise HTTPException(422, "edge.fromNode is required")
    host = _find_node(g.nodes, src)
    if host is None:
        raise HTTPException(404, "Source node not found")
    host_edges = _edges_of(host)
    if not isinstance(host_edges, list):
        setattr(host, "edges", [])
        host_edges = getattr(host, "edges")
    eid = _eid(edge_obj)
    for i, e in enumerate(host_edges):
        if _eid(e) == eid and eid is not None:
            host_edges[i] = edge_obj
            _store.save(g)
            return g
    host_edges.append(edge_obj)
    _store.save(g)
    return g

@router.delete("/{graph_id}/edges/{edge_id}", response_model=Graph, summary="Delete an edge by id, return full graph")
def delete_edge(graph_id: str, edge_id: str) -> Graph:
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

    # remove from root edges if present
    if hasattr(g, "edges") and isinstance(g.edges, list):  # type: ignore[attr-defined]
        kept = [e for e in g.edges if _eid(e) != edge_id]  # type: ignore[attr-defined]
        if len(kept) != len(g.edges):                      # type: ignore[attr-defined]
            g.edges = kept                                 # type: ignore[attr-defined]
            _store.save(g)
            return g

    # else scan attached edge lists under nodes
    def _rm(container: list[Any]) -> bool:
        changed = False
        for n in container:
            ch = _children(n)
            edges = getattr(n, "edges", None) or (n.get("edges") if isinstance(n, dict) else None)
            if isinstance(edges, list):
                newe = [e for e in edges if _eid(e) != edge_id]
                if len(newe) != len(edges):
                    setattr(n, "edges", newe) if not isinstance(n, dict) else n.__setitem__("edges", newe)
                    changed = True
            if ch and _rm(ch):
                changed = True
        return changed

    if not _rm(g.nodes):
        raise HTTPException(404, "Edge not found")
    _store.save(g)
    return g