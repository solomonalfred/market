from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field

from source.db import RoleType


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Credentials(BaseModel):
    login: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=6)


class Registration(Credentials):
    email: EmailStr = None
    first_name: Optional[str] = Field(None, max_length=64)
    last_name: Optional[str] = Field(None, max_length=64)
    role: Literal[RoleType.user, RoleType.admin] = RoleType.user


class TokenData(BaseModel):
    data: str = Field(..., min_length=3, max_length=150)
