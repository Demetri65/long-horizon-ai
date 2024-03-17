from enum import Enum
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class Base(BaseModel):
    model_config = ConfigDict(
        ser_json_timedelta="float", 
        use_enum_values=True,
        populate_by_name=True,
    )

class GoalStatus(str, Enum):
    draft = "draft"; 
    active = "active"; 
    paused = "paused"; 
    done = "done"; 
    failed = "failed"

class TaskStatus(str, Enum):
    waiting="waiting"; 
    ready="ready"; 
    running="running"; 
    blocked="blocked"; 
    paused="paused"; 
    done="done"; 
    failed="failed"

class Metric(Base):
    name: str
    unit: Literal["count","percent","score","duration","currency","custom"]
    target: float
    direction: Literal["at_least","at_most","equal"] = "at_least"