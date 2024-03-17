from typing import ClassVar, Sequence

from pydantic import BaseModel, EmailStr

from src.schemas.base import CreateBase, ResponseBase, UpdateBase


class User(ResponseBase):
    forename: str
    surname: str
    email: EmailStr
    table_name: ClassVar[str] = "user"


class UserCreate(CreateBase):
    forename: str
    surname: str
    email: EmailStr


class UserUpdate(UpdateBase):
    forename: str
    surname: str
    email: EmailStr


class ResponseMessage(ResponseBase):
    message: str


class UserSearchResults(ResponseBase):
    results: Sequence[User]
