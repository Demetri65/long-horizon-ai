from __future__ import annotations

from typing import Any, Optional, Dict
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, TypeAdapter

from src.schemas.graph import Graph                     # Pydantic Graph aggregate
from src.schemas.node import NodeUnion                  # discriminated union (kind='goal'|...)
from src.schemas.edge import EdgeUnion                  # discriminated union (kind='dependency'|...)
from src.services.graph_store import GraphStore         # thin repo: load/save/exists only
from src.services.decomposer import Decomposer          # simplified below

router = APIRouter(prefix="/graph", tags=["graph"])
_store = GraphStore()

class CreateGraphBody(BaseModel):
    graph_id: str = Field(alias="graphId")

@router.post("", response_model=Graph, summary="Create an empty graph")
def create_graph(body: CreateGraphBody) -> Graph:
    if _store.exists(body.graph_id):
        raise HTTPException(409, f"Graph '{body.graph_id}' already exists")
    g = Graph(graph_id=body.graph_id, nodes=[])  # construct with Python name, not alias
    _store.save(g)
    return g

@router.get("/{graph_id}", response_model=Graph, summary="Get full graph")
def get_graph(graph_id: str) -> Graph:
    try:
        return _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

@router.delete("/{graph_id}", summary="Delete a graph")
def delete_graph(graph_id: str) -> dict[str, Any]:
    if not _store.exists(graph_id):
        raise HTTPException(404, "Graph not found")
    g = _store.load(graph_id)
    del _store._by_id[g.graph_id]
    return {"deleted": True}

# --------------------- new: bootstrap high-level goals ---------------------

class DecomposeGoalsBody(BaseModel):
    prompt: str
    max_goals: int = Field(ge=1, le=50, default=8, alias="maxGoals")

# prebuild adapters for performance (pydantic v2 guidance)
_NODE_LIST = TypeAdapter(list[NodeUnion])
_EDGE = TypeAdapter(EdgeUnion)

@router.post(
    "/{graph_id}/llm/decompose",
    response_model=Graph,
    summary="LLM: decompose prompt into high-level GOAL nodes in chronological order; insert into graph",
)
async def decompose(graph_id: str, body: DecomposeGoalsBody, request: Request) -> Graph:
    # 0) load
    try:
        g = _store.load(graph_id)
    except KeyError:
        raise HTTPException(404, "Graph not found")

    # 1) get the LLM client from app state (configure this at startup)
    llm_client = getattr(request.app.state, "llm_client", None)
    if llm_client is None:
        # You can wire this via lifespan / startup; see notes below.
        raise HTTPException(501, "LLM client not configured on app.state.llm_client")

    # 2) ask LLM for *only* GOAL nodes, in chronological order
    decomposer = Decomposer()
    try:
        goal_nodes = await decomposer.decompose_goals(
            intent_text=body.prompt,
            llm_client=llm_client,
            max_goals=body.max_goals,
        )
    except Exception as e:
        raise HTTPException(502, f"LLM decomposition failed: {e}")

    # 3) insert nodes (upsert if you added Graph.upsert_node)
    def _nid(n: Any) -> Optional[str]:
        v = getattr(n, "node_id", None) or getattr(n, "nodeId", None)
        if v is None and isinstance(n, dict):
            v = n.get("nodeId") or n.get("node_id")
        return str(v) if v is not None else None

    inserted_ids: list[str] = []
    for n in goal_nodes:
        if hasattr(g, "upsert_node"):
            g.upsert_node(n)  # aggregate method if you added it
        else:
            g.nodes.append(n)  # fallback: append as root
        nid = _nid(n)
        if nid:
            inserted_ids.append(nid)

    # 4) add simple sequential dependency edges (Goal[i] -> Goal[i+1])
    #    This encodes the chronological order without planning details yet.
    def _find_node(container: list[Any], node_id: str) -> Optional[Any]:
        for nn in container:
            cid = _nid(nn)
            if cid == node_id:
                return nn
            ch = getattr(nn, "nodes", None) or (nn.get("nodes") if isinstance(nn, dict) else None)
            if isinstance(ch, list):
                hit = _find_node(ch, node_id)
                if hit is not None:
                    return hit
        return None

    def _edges_of(n: Any) -> list[Any]:
        ch = getattr(n, "edges", None)
        if ch is None and isinstance(n, dict):
            ch = n.get("edges")
        if not isinstance(ch, list):
            # materialize edges list
            try:
                setattr(n, "edges", [])
                ch = getattr(n, "edges")
            except Exception:
                if isinstance(n, dict):
                    n["edges"] = []
                    ch = n["edges"]
                else:
                    raise
        return ch

    for i in range(len(inserted_ids) - 1):
        src, dst = inserted_ids[i], inserted_ids[i + 1]
        edge_dict: Dict[str, Any] = {
            "kind": "dependency",
            "edgeId": f"E-{graph_id}-{i+1}",
            "fromNode": src,
            "toNode": dst,
            "constraint": "FS",
            "lagHours": 0,
            "hard": False,
        }
        edge_obj = _EDGE.validate_python(edge_dict)  # strict
        host = _find_node(g.nodes, src)
        if host is not None:
            _edges_of(host).append(edge_obj)

    # 5) save and return updated graph
    _store.save(g)
    return g