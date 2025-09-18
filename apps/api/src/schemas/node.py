from typing import Annotated, Literal, Union, List
from pydantic import ConfigDict, Field
from src.config import ModelBase
from .common import NodeId
from .enums import NodeKind, NodeStatus
from .smarter import SmarterForGoal, SmarterForMilestone, SmarterForTask
from .edge import EdgeBase, EdgeUnion

class NodeBase(ModelBase):
    node_id: NodeId = Field(..., alias="nodeId")
    title: str = Field(..., alias="title")
    status: NodeStatus = Field(NodeStatus.not_started, alias="status")
    parent: NodeId | None = Field(None, alias="parent")
    nodes: List['GoalNode'] = Field(default_factory=list, alias="nodes")
    edges: List[EdgeBase] = Field(default_factory=list, alias="edges")

class GoalNode(NodeBase):
    model_config = ConfigDict(extra='forbid')
    kind: Literal["goal"] = "goal"
    smarter: SmarterForGoal

class MilestoneNode(NodeBase):
    model_config = ConfigDict(extra='forbid')
    kind: Literal["milestone"] = "milestone"
    smarter: SmarterForMilestone

class TaskNode(NodeBase):
    model_config = ConfigDict(extra='forbid')
    kind: Literal["task"] = "task"
    smarter: SmarterForTask

NodeUnion = GoalNode
# NodeUnion = Annotated[
#     Union[GoalNode, MilestoneNode, TaskNode],
#     Field(discriminator='kind')
# ]