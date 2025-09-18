from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

class ApiModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid", 
        validate_default=True, 
        str_strip_whitespace=True
    )

class ValidateIssue(ApiModel):
    code: Literal[
        "unknown-node",
        "duplicate-node",
        "unknown-edge-node",
        "missing-contrib-metric",
        "cycle-detected"
    ]
    message: str
    path: Optional[List[str]] = None   
    
class ValidateResponse(ApiModel):
    ok: bool
    issues: List[ValidateIssue] = Field(default_factory=list)

class TraverseResponse(ApiModel):
    order: List[str]           # visited nodeIds in traversal order
    visited: int

class TopoResponse(ApiModel):
    order: List[str]           # topologically sorted nodeIds (dependency DAG)
    cycles: Optional[List[List[str]]] = None  # present if cycle detection enabled

class CriticalPathNode(ApiModel):
    node_id: str = Field(alias="nodeId")
    earliest_start: Optional[str] = None
    latest_finish: Optional[str] = None

class CriticalPathResponse(ApiModel):
    path: List[CriticalPathNode] = Field(default_factory=list)
    total_lag_hours: Optional[int] = None

class RollupResponse(ApiModel):
    # metricId -> rolled-up value (number | string | boolean)
    metrics: Dict[str, Any] = Field(default_factory=dict)


class BulkNodesRequest(ApiModel):
    nodes: List[Any]  # accept NodeUnion JSON; validation happens in endpoint (schemas.node.NodeUnion)

class BulkEdgesRequest(ApiModel):
    edges: List[Any]  # accept EdgeUnion JSON; validation happens in endpoint (schemas.edge.EdgeUnion)

class BulkWriteResponse(ApiModel):
    nodes_upserted: int = 0
    edges_upserted: int = 0