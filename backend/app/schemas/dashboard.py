from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.player import PlayerListItemResponse
from app.schemas.fixture import GameResponse, SO5FixtureResponse
from app.schemas.market import MarketOpportunity
from app.schemas.alert import AlertResponse


class DashboardGameweekInfo(BaseModel):
    game_week: int
    event_name: str
    state: str
    start_date: datetime
    end_date: datetime
    cutoff_date: Optional[datetime] = None
    time_remaining_seconds: Optional[int] = None


class DashboardDataFreshness(BaseModel):
    last_sync_at: Optional[datetime] = None
    status: str = "fresh"  # fresh, syncing, stale, offline
    sync_jobs_summary: dict = {}


class DashboardMetricsResponse(BaseModel):
    current_gameweek: Optional[DashboardGameweekInfo] = None
    squad_value_eur: float = 0.0
    average_score_l5: float = 0.0
    players_in_form: List[PlayerListItemResponse] = []
    players_at_risk: List[PlayerListItemResponse] = []
    market_opportunities: List[MarketOpportunity] = []
    scouting_opportunities: List[PlayerListItemResponse] = []
    upcoming_fixtures: List[GameResponse] = []
    recent_alerts: List[AlertResponse] = []
    data_freshness: DashboardDataFreshness
