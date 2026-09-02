from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PlayerGameScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    player_id: int
    game_id: int
    score: Optional[float] = None
    average_score: Optional[float] = None
    projected_score: Optional[float] = None
    projection_grade: Optional[str] = None
    projection_reliability: Optional[float] = None
    decisive_score: Optional[float] = None
    all_around_score: Optional[float] = None
    score_status: Optional[str] = None
    scoring_version: Optional[str] = None
    created_at: Optional[datetime] = None


class ScoreSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    player_id: int
    l5_average: Optional[float] = None
    l15_average: Optional[float] = None
    l40_average: Optional[float] = None
    clean_sheet_rate: Optional[float] = None
    goal_rate: Optional[float] = None
    assist_rate: Optional[float] = None
    observed_at: datetime
