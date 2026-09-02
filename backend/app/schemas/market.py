from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.card import CardResponse, PriceSnapshotResponse


class MarketMover(BaseModel):
    player_id: int
    player_name: str
    club_name: Optional[str] = None
    position: str
    image_url: Optional[str] = None
    current_price: float
    previous_price: float
    change_pct: float
    volume_24h: Optional[float] = 0.0
    currency: str = "EUR"


class MarketOpportunity(BaseModel):
    player_id: int
    player_name: str
    club_name: Optional[str] = None
    position: str
    image_url: Optional[str] = None
    current_price: float
    fair_value: float
    discount_pct: float
    scout_score: float
    recommendation: str
    confidence: float
    reason: str
    currency: str = "EUR"


class TrendingCard(BaseModel):
    card_id: int
    player_id: int
    player_name: str
    rarity: str
    current_price: float
    trades_count: int
    volume_24h: float
    image_url: Optional[str] = None
    currency: str = "EUR"


class PlayerMarketOverview(BaseModel):
    player_id: int
    display_name: str
    current_floor_price: Optional[float] = None
    avg_price_7d: Optional[float] = None
    avg_price_30d: Optional[float] = None
    change_7d_pct: Optional[float] = 0.0
    change_30d_pct: Optional[float] = 0.0
    volume_30d: Optional[float] = 0.0
    currency: str = "EUR"
    price_history: List[PriceSnapshotResponse] = []
    cards: List[CardResponse] = []


class MarketSummaryResponse(BaseModel):
    total_volume_24h: float
    active_listings_count: int
    top_gainers: List[MarketMover] = []
    top_losers: List[MarketMover] = []
    opportunities: List[MarketOpportunity] = []
    trending: List[TrendingCard] = []
