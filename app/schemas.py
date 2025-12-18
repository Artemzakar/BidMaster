from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Схемы для предметов (CRUD)
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    year_created: int
    owner_id: int

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    # Делаем поля необязательными для обновления
    title: Optional[str] = None
    year_created: Optional[int] = None
    owner_id: Optional[int] = None

class ItemResponse(ItemBase):
    item_id: int
    is_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True


class AuctionResponse(BaseModel):
    auction_id: int
    item_id: int
    start_price: float
    current_price: float
    status: str
    start_time: datetime
    end_time: datetime

    class Config:
        orm_mode = True