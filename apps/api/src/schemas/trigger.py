from typing import Optional, Literal
from .common import Base

class Trigger(Base):
    kind: Literal["time","schedule","webhook","data_change","manual"]
    cron: Optional[str] = None
    temporal_schedule_id: Optional[str] = None
    resource: Optional[str] = None