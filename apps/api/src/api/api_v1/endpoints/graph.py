from __future__ import annotations

import json
from typing import Any, Optional, Dict
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
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
        raise HTTPException(501, "LLM client not configured on app.state.llm_client")

    # 2) ask LLM for *only* GOAL nodes, in chronological order
    decomposer = Decomposer()
    try:
        goal_nodes = await decomposer.decompose_goals(
            intent_text=body.prompt,
            llm_client=llm_client,
            max_goals=body.max_goals,
            text_format=Graph,  # pass text format if needed
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

@router.post(
    "/{graph_id}/llm/decompose:stream",
    summary="Stream text deltas while decomposing goals; then persist nodes"
)
async def decompose_stream(graph_id: str, body: DecomposeGoalsBody, request: Request):
        # 0) load or 404
        try:
            g = _store.load(graph_id)
        except KeyError:
            raise HTTPException(404, "Graph not found")

        # 1) get LLM client
        llm_client = getattr(request.app.state, "llm_client", None)
        if llm_client is None:
            raise HTTPException(501, "LLM client not configured on app.state.llm_client")

        # 2) build the same "goals-only" prompt you already use
        from src.services.policies import SYSTEM_POLICY, build_user_prompt
        user_prompt = build_user_prompt(body.prompt, max_nodes=body.max_goals) + (
            "\n\nSTRICT OUTPUT RULES:\n"
            "- Return ONLY top-level GOAL nodes (kind='goal').\n"
            "- Order nodes chronologically (earliest first).\n"
            "- Do NOT include milestones or tasks yet.\n"
            "- If uncertain about dates, still order by logical sequence.\n"
            "- Output JSON with one top-level key: 'nodes'. \n"
            "- 'edges' within 'nodes' MUST not be omitted or empty and must connect nodes correctly.\n"
        )

        async def gen():
            # Keep deltas so we can fall back to JSON parsing if needed
            chunks: list[str] = []

            # 3) stream deltas token-by-token
            client = llm_client.client
            model = llm_client.model
            async with client.responses.stream(
                model=model,
                input=[
                    {"role": "system", "content": SYSTEM_POLICY},
                    {"role": "user",   "content": user_prompt},
                ],
                # optional: if your model is trained to emit JSON matching your pydantic Graph
                # you can pass text_format=Graph here; we will still read output_parsed later
                # text_format=Graph,
            ) as stream:
                async for event in stream:
                    et = getattr(event, "type", "")
                    if et in ("response.output_text.delta", "response.text.delta"):
                        delta = getattr(event, "delta", "") or ""
                        if delta:
                            chunks.append(delta)
                            # plain-text protocol: stream raw text bytes
                            yield delta
                    elif et == "response.error":
                        err = getattr(event, "error", "Unknown stream error")
                        yield f"\n[error] {err}\n"

                # 4) stream finished — parse and persist goals defensively
                final = await stream.get_final_response()
                parsed = getattr(final, "output_parsed", None)

                data: dict[str, Any] | None = None
                if isinstance(parsed, dict):
                    data = parsed
                else:
                    # try to parse the accumulated text into JSON
                    txt = "".join(chunks).strip()
                    if txt:
                        try:
                            data = json.loads(txt)
                        except json.JSONDecodeError:
                            data = None

                # Only persist if we got {"nodes":[...]}
                if isinstance(data, dict) and "nodes" in data:
                    try:
                        nodes: list[NodeUnion] = _NODE_LIST.validate_python(data["nodes"])
                        goals_only = [n for n in nodes if getattr(n, "kind", None) == "goal"]
                        if len(goals_only) > body.max_goals:
                            goals_only = goals_only[: body.max_goals]

                        # Insert nodes (same as your JSON endpoint)
                        def _nid(n: Any) -> Optional[str]:
                            v = getattr(n, "node_id", None) or getattr(n, "nodeId", None)
                            if v is None and isinstance(n, dict):
                                v = n.get("nodeId") or n.get("node_id")
                            return str(v) if v is not None else None

                        inserted_ids: list[str] = []
                        for n in goals_only:
                            if hasattr(g, "upsert_node"):
                                g.upsert_node(n)
                            else:
                                g.nodes.append(n)
                            nid = _nid(n)
                            if nid:
                                inserted_ids.append(nid)

                        # Add simple sequential dependency edges Goal[i] -> Goal[i+1]
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
                            edge_obj = _EDGE.validate_python(edge_dict)
                            host = _find_node(g.nodes, src)
                            if host is not None:
                                _edges_of(host).append(edge_obj)

                        _store.save(g)
                    except Exception:
                        # Persisting failed — do not break the stream
                        # (optionally log this)
                        pass

       
        return StreamingResponse(gen(), media_type="text/plain; charset=utf-8")