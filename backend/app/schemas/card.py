from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.common import RarityEnum


class CardPriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    card_id: int
    price: float
    currency: str
    source: str
    observed_at: datetime


class CardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sorare_id: Optional[str] = None
    asset_id: Optional[str] = None
    player_id: int
    season_year: int
    rarity: RarityEnum
    position: Optional[str] = None
    power: Optional[float] = 0.0
    grade: Optional[str] = None
    image_url: Optional[str] = None
    latest_price: Optional[float] = None
    currency: Optional[str] = "EUR"

class CardWithPlayerResponse(CardResponse):
    player: Optional[dict] = None


class PriceSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    player_id: int
    card_id: Optional[int] = None
    average_price: float
    lowest_ask: Optional[float] = None
    highest_bid: Optional[float] = None
    volume_24h: Optional[float] = None
    currency: str
    observed_at: datetime
