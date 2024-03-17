from typing import List, Optional
from pydantic import Field
from .common import Base, TaskStatus
from .checkpoint import Checkpoint
from .policy import AutonomyPolicy

class Task(Base):
    id: str
    title: str
    status: TaskStatus = TaskStatus.waiting
    owner_user_id: Optional[str] = None
    depends_on: List[str] = []
    checkpoints: List[Checkpoint] = []
    autonomy: AutonomyPolicy = AutonomyPolicy()
    est_duration: Optional[float] = Field(default=None, description="Estimated seconds")
    notes: Optional[str] = None