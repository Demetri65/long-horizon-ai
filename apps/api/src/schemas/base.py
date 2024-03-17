from typing import ClassVar, Optional
from pydantic import BaseModel, ConfigDict

# Shared properties
# class CRUDBaseModel(BaseModel):
#     # where the data
#     table_name: str


# Properties to receive on item creation
# in
class CreateBase(BaseModel):
    # inherent to add more properties for creating
    pass


# Properties to receive on item update
# in
class UpdateBase(BaseModel):
    # inherent to add more properties for updating
    id: str


# response
# Properties shared by models stored in DB (optional so concrete models don't have to include them)
class InDBBase(BaseModel):
    id: str
    user_id: Optional[str] = None
    created_at: Optional[str] = None


# Properties to return to client
# crud model
# out
class ResponseBase(InDBBase):
    # inherent to add more properties for responding
    table_name: ClassVar[str] = "ResponseBase".lower()
    Config: ClassVar[ConfigDict] = ConfigDict(
        extra="ignore", arbitrary_types_allowed=True
    )
