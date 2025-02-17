from typing import Literal
from pydantic import BaseModel, Field

from source.db.role_types import RoleType
from source.routers.shemas.auth import Registration


class AdminUser(Registration):
    coins_amount: int = Field(..., ge=0)


class UpdateUser(BaseModel):
    login: str = Field(..., min_length=3, max_length=150)
    coin_amount: int = Field(..., ge=0)
    role: Literal[RoleType.user, RoleType.admin] = RoleType.user


class MerchInfo(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    price: int = Field(..., ge=0)
