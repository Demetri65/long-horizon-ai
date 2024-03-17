from datetime import datetime
from typing import List, Optional
from .common import Base, GoalStatus, Metric
from .trigger import Trigger
from .policy import AutonomyPolicy
from .task import Task

class Goal(Base):
    id: str
    title: str
    scope: Optional[str] = None
    success: Optional[Metric] = None
    deadline: Optional[datetime] = None
    status: GoalStatus = GoalStatus.active
    subgoals: List["Goal"] = []
    tasks: List[Task] = []
    autonomy: AutonomyPolicy = AutonomyPolicy()
    triggers: List[Trigger] = []