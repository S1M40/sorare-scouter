from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.club import ClubResponse
from app.schemas.competition import CompetitionResponse


class GameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sorare_id: Optional[str] = None
    home_club_id: int
    away_club_id: int
    competition_id: int
    date: datetime
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    minute: Optional[int] = None
    coverage_status: Optional[str] = None
    home_club: Optional[ClubResponse] = None
    away_club: Optional[ClubResponse] = None
    competition: Optional[CompetitionResponse] = None


class SO5FixtureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sorare_id: Optional[str] = None
    event: Optional[str] = None
    event_name: str
    event_type: Optional[str] = None
    game_week: int
    start_date: datetime
    end_date: datetime
    cutoff_date: Optional[datetime] = None
    state: str


class FixtureDetailResponse(BaseModel):
    fixture: SO5FixtureResponse
    games: list[GameResponse] = []
