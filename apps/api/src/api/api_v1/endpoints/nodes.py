from __future__ import annotations

from typing import Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import TypeAdapter
from src.schemas.node import NodeUnion
from src.schemas.graph import Graph
from src.services.graph_store import GraphStore

router = APIRouter(prefix="/graphs", tags=["nodes"])
_store = GraphStore()
_NODE = TypeAdapter(NodeUnion)

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

def _find(container: list[Any], node_id: str) -> Optional[Any]:
    for n in container:
        if _nid(n) == node_id:
            return n
        ch = _children(n)
        hit = _find(ch, node_id) if ch else None
        if hit is not None:
            return hit
    return None

@router.get("/{graph_id}/nodes/{node_id}", response_model=NodeUnion, summary="Get a node")
def get_node(graph_id: str, node_id: str) -> NodeUnion:
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")
    n = _find(g.nodes, node_id)
    if n is None:
        raise HTTPException(404, "Node not found")
    return n

@router.post("/{graph_id}/nodes", response_model=Graph, summary="Upsert a single node, return full graph")
def upsert_node(graph_id: str, node: dict) -> Graph:
    node_obj = _NODE.validate_python(node)
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

    if hasattr(g, "upsert_node"):
        g.upsert_node(node_obj)  # aggregate method
    else:
        # trivial fallback: append as root
        g.nodes.append(node_obj)
    _store.save(g)
    return g

@router.delete("/{graph_id}/nodes/{node_id}", response_model=Graph, summary="Delete a node (and detach edges)")
def delete_node(graph_id: str, node_id: str) -> Graph:
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

    def _delete(container: list[Any]) -> bool:
        for i, n in enumerate(container):
            if _nid(n) == node_id:
                del container[i]
                return True
            ch = _children(n)
            if ch and _delete(ch):
                return True
        return False

    if not _delete(g.nodes):
        raise HTTPException(404, "Node not found")
    _store.save(g)
    return g