from __future__ import annotations
from fastapi import APIRouter, HTTPException, Request, logger

from typing import Any, List, Dict
from httpx import request
from pydantic import TypeAdapter

from src.schemas.node import NodeUnion
from src.schemas.edge import EdgeUnion  
from src.services.policies import SYSTEM_POLICY, build_user_prompt  

_NODE_LIST = TypeAdapter(list[NodeUnion])

class Decomposer:
    """
    LLM-facing adapter:
      - Builds a 'goals-only' prompt
      - Validates the returned nodes as NodeUnion[]
      - Filters to GOALs only (defensive)
    """

    async def decompose_goals(
        self,
        intent_text: str,
        llm_client: Any, 
        max_goals: int = 8,
        text_format: Any = None,
    ) -> List[NodeUnion]:
        """
        Returns a list of GOAL nodes, in chronological order.
        No milestones/tasks yet. The endpoint will add simple dependency edges.
        """

        user_prompt = build_user_prompt(intent_text, max_nodes=max_goals)

        user_prompt += (
            "\n\nSTRICT OUTPUT RULES:\n"
            "- Return ONLY top-level GOAL nodes (kind='goal').\n"
            "- Order nodes chronologically (earliest first).\n"
            "- Do NOT include milestones or tasks yet.\n"
            "- If uncertain about dates, still order by logical sequence.\n"
            "- Output JSON with one top-level key: 'nodes'. 'edges' MUST be omitted or empty.\n"
        )
        
        
        # 3) call LLM: it must return JSON with 'nodes' (array)
        result = await llm_client.generate_json(system=SYSTEM_POLICY, user=user_prompt, text_format=text_format)
        if not isinstance(result, dict) or "nodes" not in result:
            raise ValueError(result, "LLM did not return an object with a 'nodes' array")

        # 4) validate strictly; then filter to GOAL nodes (defensive)
        nodes: List[NodeUnion] = _NODE_LIST.validate_python(result["nodes"])
        goals_only: List[NodeUnion] = [n for n in nodes if getattr(n, "kind", None) == "goal"]

        if not goals_only:
            raise ValueError(nodes, "No GOAL nodes returned by LLM")

        # (Optional) sanity: enforce <= max_goals
        if len(goals_only) > max_goals:
            goals_only = goals_only[:max_goals]

        return goals_only