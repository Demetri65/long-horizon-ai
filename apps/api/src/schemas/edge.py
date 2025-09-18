from typing import Annotated, Literal, Union, List
from pydantic import Field
from src.config import ModelBase
from .common import EdgeId, NodeId, ISODateTime
from .enums import EdgeKind, EdgeStatus
from .smarter import MetricId

class EdgeBase(ModelBase):
    edge_id: EdgeId = Field(..., alias="edgeId")
    from_node: NodeId = Field(..., alias="fromNode")
    to_node: NodeId = Field(..., alias="toNode")
    label: str | None = Field(None, alias="label")
    status: EdgeStatus = Field(EdgeStatus.active, alias="status")
    created_at: ISODateTime | None = Field(None, alias="createdAt")
    updated_at: ISODateTime | None = Field(None, alias="updatedAt")

class DependencyEdge(EdgeBase):
    kind:  Literal["dependency"] = "dependency"
    constraint: Annotated[str, Field(pattern="^(FS|SS|FF|SF)$")] = "FS"
    lag_hours: int = 0
    hard: bool = False
    earliest_start: ISODateTime | None = None
    latest_finish: ISODateTime | None = None

class ContributesToEdge(EdgeBase):
    kind: Literal["contributes_to"] = "contributes_to"
    weight: float = Field(ge=0.0, le=1.0, default=0.0)
    metric_ids: List[MetricId] = []
    aggregation: Annotated[str, Field(pattern="^(weighted_sum|avg|min|max|boolean_or)$")] = "weighted_sum"

class RelatesToEdge(EdgeBase):
    kind: Literal["relates_to"] = "relates_to"
    tags: list[str] = []
    rationale: str | None = None

class ValidatesEdge(EdgeBase):
    kind: Literal["validates"] = "validates"
    based_on_eval_ids: list[int] = []
    criteria: list[str] = []
    passed: bool | None = None

EdgeUnion = DependencyEdge

# EdgeUnion = Annotated[
#     Union[DependencyEdge, ContributesToEdge, RelatesToEdge, ValidatesEdge],
#     Field(discriminator='kind')
# ]