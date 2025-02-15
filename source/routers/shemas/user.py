from typing import Dict, List, Tuple
from pydantic import BaseModel, Field


class UserHistory(BaseModel):
    coins: int = 0,
    inventory: List[Tuple[str, int]] = list(),
    coinHistory: Dict[str, List[Tuple[str, int]]]

class SendCoin(BaseModel):
    toUser: str = Field(..., min_length=3, max_length=150)
    amount: int = Field(..., ge=0)

class ItemInfo(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)

class ResponseMessage(BaseModel):
    description: str
