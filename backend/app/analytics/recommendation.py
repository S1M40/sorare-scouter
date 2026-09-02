from typing import List
from app.schemas.common import RecommendationEnum, RiskLevelEnum
from app.schemas.metric import RecommendationDetail, RiskFactor


def generate_recommendation(
    scout_score: float,
    form_score: float,
    minutes_score: float,
    fixture_score: float,
    availability_score: float,
    market_score: float,
    risk_level: RiskLevelEnum,
    risk_factors: List[RiskFactor],
) -> RecommendationDetail:
    """Generate explainable scouting recommendation with deterministic reasons and risks."""
    reasons: List[str] = []
    risks: List[str] = [rf.message for rf in risk_factors]

    # Evaluate positive drivers
    if form_score >= 70.0:
        reasons.append("Strong recent form and decisive impact")
    elif form_score >= 55.0:
        reasons.append("Steady scoring foundation")

    if minutes_score >= 80.0:
        reasons.append("High expected minutes as undisputed starter")

    if fixture_score >= 70.0:
        reasons.append("Favorable upcoming fixture schedule")

    if market_score >= 75.0:
        reasons.append("Market price attractive / trading below 30-day average")

    if availability_score >= 90.0:
        reasons.append("Clean medical and disciplinary record")

    # Decision Matrix
    if risk_level == RiskLevelEnum.CRITICAL or availability_score == 0.0:
        recommendation = RecommendationEnum.AVOID
        confidence = 90.0
        if not reasons:
            reasons.append("Player is currently sidelined")
    elif scout_score >= 75.0 and risk_level in (RiskLevelEnum.LOW, RiskLevelEnum.MEDIUM):
        recommendation = RecommendationEnum.BUY
        confidence = round(min(92.0, 70.0 + (scout_score * 0.2)), 1)
        if not reasons:
            reasons.append("Top overall scout score profile")
    elif scout_score >= 62.0 and risk_level != RiskLevelEnum.HIGH:
        recommendation = RecommendationEnum.WATCH
        confidence = 80.0
        if not reasons:
            reasons.append("Promising profile, monitor entry price")
    elif risk_level == RiskLevelEnum.HIGH or (market_score < 35.0 and form_score < 50.0):
        recommendation = RecommendationEnum.SELL
        confidence = 82.0
        reasons.append("Declining metrics and high current risk profile")
    else:
        recommendation = RecommendationEnum.HOLD
        confidence = 75.0
        if not reasons:
            reasons.append("Stable performance metrics with balanced risk")

    return RecommendationDetail(
        recommendation=recommendation,
        scout_score=scout_score,
        confidence=confidence,
        reasons=reasons,
        risks=risks,
    )
