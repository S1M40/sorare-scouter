from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common import RecommendationEnum, RiskLevelEnum, SourceTypeEnum


class RiskFactor(BaseModel):
    category: str
    severity: RiskLevelEnum
    message: str
    source_type: SourceTypeEnum = SourceTypeEnum.FACT


class StartingXIPrediction(BaseModel):
    starting_probability: float = Field(..., ge=0, le=100, description="Deterministic 0-100 starting probability")
    label: str = "PREDICTION"
    confidence: float = Field(..., ge=0, le=100)
    expected_role: str = "Starter"  # Starter, Rotation, Bench, Out
    factors: List[str] = []


class RecommendationDetail(BaseModel):
    recommendation: RecommendationEnum
    scout_score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=100)
    reasons: List[str] = []
    risks: List[str] = []


class PlayerMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    player_id: int
    form_score: float = Field(..., ge=0, le=100)
    consistency_score: float = Field(..., ge=0, le=100)
    minutes_score: float = Field(..., ge=0, le=100)
    fixture_score: float = Field(..., ge=0, le=100)
    market_score: float = Field(..., ge=0, le=100)
    availability_score: float = Field(..., ge=0, le=100)
    scout_score: float = Field(..., ge=0, le=100)
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevelEnum
    starting_probability: float = Field(..., ge=0, le=100)
    recommendation: RecommendationEnum
    confidence: float = Field(..., ge=0, le=100)
    calculated_at: datetime
    
    # Detailed explainability objects
    starting_prediction: Optional[StartingXIPrediction] = None
    recommendation_detail: Optional[RecommendationDetail] = None
    risk_factors: List[RiskFactor] = []
