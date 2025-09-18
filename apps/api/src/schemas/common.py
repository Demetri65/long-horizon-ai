from datetime import datetime
from typing import Annotated
from pydantic import Field, constr
from src.config import ModelBase

NodeId = Annotated[str, Field(pattern=r"^[A-Za-z0-9_\-:.]{1,64}$")]
EdgeId = Annotated[str, Field(pattern=r"^[A-Za-z0-9_\-:.]{1,64}$")]
MetricId = Annotated[str, Field(min_length=1, max_length=64)]

ISODateTime = datetime

class WithTimestamps(ModelBase):
    created_at: ISODateTime | None = None
    updated_at: ISODateTime | None = None