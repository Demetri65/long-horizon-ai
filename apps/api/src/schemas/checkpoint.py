from datetime import datetime
from typing import Optional
from pydantic import Field
from .common import Base, Metric

class Checkpoint(Base):
    id: str
    title: str
    due: Optional[datetime] = None
    measure: Optional[Metric] = None
    notes: Optional[str] = None
    pct_complete: Optional[float] = Field(default=None, ge=0, le=100)