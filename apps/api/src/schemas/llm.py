from pydantic import BaseModel
from typing import Optional

from schemas.graph import Graph

class LLMRequest(BaseModel):
    """Request body for /llm/structure"""
    input: str
    style: Optional[str] = None
    max_goals: Optional[int] = None

class LLMResponse(BaseModel):
    """Response body for /llm/structure"""
    plan: Graph