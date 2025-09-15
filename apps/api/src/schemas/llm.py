from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal

class Base(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        ser_json_timedelta="float",
        populate_by_name=True,
    )

class PlanStep(Base):
    id: str
    title: str
    detail: Optional[str] = None

class Node(Base):
    id: str
    label: str
    kind: Literal["goal","subgoal","task","checkpoint"] = "task"

class Edge(Base):
    source: str
    target: str
    relation: Literal["decomposes","depends_on"] = "depends_on"

class StructuredPlan(Base):
    steps: List[PlanStep]
    final_prompt: str
    nodes: Optional[List[Node]] = None
    edges: Optional[List[Edge]] = None

class LLMRequest(Base):
    input: str
    style: Optional[str] = None
    max_steps: Optional[int] = Field(default=8, ge=1, le=30)

class LLMResponse(Base):
    plan: StructuredPlan
