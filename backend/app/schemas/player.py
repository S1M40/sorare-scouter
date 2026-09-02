from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.club import ClubResponse
from app.schemas.injury import InjuryResponse
from app.schemas.suspension import SuspensionResponse
from app.schemas.card import CardResponse
from app.schemas.score import PlayerGameScoreResponse
from app.schemas.metric import PlayerMetricResponse
from app.schemas.common import PositionEnum, RecommendationEnum, RiskLevelEnum


class PlayerListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sorare_id: Optional[str] = None
    slug: str
    display_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    position: str
    nationality: Optional[str] = None
    image_url: Optional[str] = None
    club: Optional[ClubResponse] = None
    
    # Analytics summary
    scout_score: Optional[float] = 0.0
    form_score: Optional[float] = 0.0
    starting_probability: Optional[float] = 50.0
    recommendation: Optional[RecommendationEnum] = RecommendationEnum.HOLD
    risk_level: Optional[RiskLevelEnum] = RiskLevelEnum.LOW
    current_floor_price: Optional[float] = None
    currency: Optional[str] = "EUR"
    is_injured: bool = False
    is_suspended: bool = False


class PlayerDetailResponse(PlayerListItemResponse):
    metric: Optional[PlayerMetricResponse] = None
    active_injuries: List[InjuryResponse] = []
    active_suspensions: List[SuspensionResponse] = []
    recent_scores: List[PlayerGameScoreResponse] = []
    cards: List[CardResponse] = []


class PlayerFilterParams(BaseModel):
    search: Optional[str] = None
    position: Optional[str] = None
    club: Optional[str] = None
    competition: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    score_min: Optional[float] = None
    score_max: Optional[float] = None
    form_min: Optional[float] = None
    starting_probability_min: Optional[float] = None
    injury_status: Optional[str] = None  # all, fit, injured, suspended
    recommendation: Optional[str] = None  # BUY, WATCH, HOLD, SELL, AVOID
    sort_by: Optional[str] = "scout_score"  # scout_score, form_score, price, age, name, starting_probability
    sort_order: Optional[str] = "desc"  # asc, desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)
