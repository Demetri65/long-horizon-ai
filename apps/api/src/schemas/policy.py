from typing import List, Literal, Optional
from enum import Enum
from .common import Base

class AutonomyLevel(str, Enum):
    none="none"; 
    tool_call="tool_call"; 
    draft="draft"; 
    execute="execute"

class Recipient(Base):
    kind: Literal["person","channel","service"]
    address: str
    label: Optional[str] = None

class ToolSpec(Base):
    name: str
    version: Optional[str] = None
    allowed_actions: List[str] = []  # e.g., ["calendar.read","email.draft"]

class AutonomyPolicy(Base):
    level: AutonomyLevel = AutonomyLevel.none
    tools: List[ToolSpec] = []
    recipients: List[Recipient] = []
    requires_approval: List[str] = []