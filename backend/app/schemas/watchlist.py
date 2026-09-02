from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.player import PlayerListItemResponse


class WatchlistCreate(BaseModel):
    target_price: Optional[float] = None
    notes: Optional[str] = None


class WatchlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    player_id: int
    target_price: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    player: Optional[PlayerListItemResponse] = None
