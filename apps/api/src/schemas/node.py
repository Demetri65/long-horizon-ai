from typing import Annotated, Literal, Union, List
from pydantic import Field
from src.config import ModelBase
from .common import NodeId
from .enums import NodeKind, NodeStatus
from .smarter import SmarterForGoal, SmarterForMilestone, SmarterForTask
from .edge import EdgeUnion

class NodeBase(ModelBase):
    node_id: NodeId = Field(..., alias="nodeId")
    title: str = Field(..., alias="title")
    status: NodeStatus = Field(NodeStatus.not_started, alias="status")
    parent: NodeId | None = Field(None, alias="parent")
    nodes: List['NodeUnion'] = Field(default_factory=list, alias="nodes")     # children (recursive)
    edges: List[EdgeUnion] = Field(default_factory=list, alias="edges")       # outgoing edges only

class GoalNode(NodeBase):
    kind: Literal["goal"] = "goal"
    smarter: SmarterForGoal

class MilestoneNode(NodeBase):
    kind: Literal["milestone"] = "milestone"
    smarter: SmarterForMilestone

class TaskNode(NodeBase):
    kind: Literal["task"] = "task"
    smarter: SmarterForTask

NodeUnion = Annotated[
    Union[GoalNode, MilestoneNode, TaskNode],
    Field(discriminator='kind')
]