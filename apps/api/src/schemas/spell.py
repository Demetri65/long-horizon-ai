from typing import ClassVar, Sequence

from pydantic import BaseModel

from src.schemas.base import CreateBase, ResponseBase, UpdateBase


class Spell(ResponseBase):
    name: str
    description: str
    table_name: ClassVar[str] = "spells"


class SpellCreate(CreateBase):
    id: str
    name: str
    description: str


class SpellUpdate(UpdateBase):
    name: str
    description: str


class SpellSearchResults(ResponseBase):
    results: Sequence[Spell]
