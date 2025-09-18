from __future__ import annotations

from typing import Final
from pydantic import TypeAdapter
from src.schemas.node import NodeUnion 
from src.schemas.edge import EdgeUnion  
from src.schemas.enums import NodeKind, EdgeKind, NodeStatus 

SYSTEM_POLICY: Final[str] = """\
You are a planner. Output ONLY valid JSON, no commentary.
JSON must contain two top-level arrays: "nodes" and "edges".
Every node must conform to the Node union schema with a 'kind' discriminator.
Every edge must conform to the Edge union schema with a 'kind' discriminator.
Do not invent fields. Use enum values exactly as listed in the schema.
"""

# Build strict JSON Schemas that the model must follow (for few-shot or tool use).
NODE_SCHEMA: Final[dict] = TypeAdapter(list[NodeUnion]).json_schema() 
EDGE_SCHEMA: Final[dict] = TypeAdapter(list[EdgeUnion]).json_schema() 

# Compose the user prompt dynamically so enums are always in sync with code.
def build_user_prompt(goal_text: str, max_nodes: int = 15) -> str:
    kinds = ", ".join(k.value for k in NodeKind)
    ekinds = ", ".join(k.value for k in EdgeKind)
    statuses = ", ".join(s.value for s in NodeStatus)

    return f"""\
Decompose the following high-level intent into a small goal graph (<= {max_nodes} nodes).

INTENT:
{goal_text}

CONSTRAINTS:
- Nodes MUST use kinds: {kinds}
- Edges MUST use kinds: {ekinds}
- Node status MUST be one of: {statuses}
- For contributes_to, metricIds MUST refer to metricIds on the TARGET goal.
- For dependency, respect causal order (no cycles).

RESPONSE FORMAT (STRICT):
{{
  "nodes": [ NodeUnion, ... ],
  "edges": [ EdgeUnion, ... ]
}}

JSON SCHEMAS:
"nodes": {NODE_SCHEMA}
"edges": {EDGE_SCHEMA}
"""