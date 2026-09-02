from typing import List, Optional
from datetime import datetime, timezone
from app.analytics.form import calculate_form_score
from app.analytics.consistency import calculate_consistency_score
from app.analytics.minutes import calculate_minutes_score
from app.analytics.fixture import calculate_fixture_score
from app.analytics.availability import calculate_availability_score
from app.analytics.market import calculate_market_score
from app.analytics.scout_score import calculate_scout_score
from app.analytics.starting_probability import calculate_starting_probability
from app.analytics.risk_engine import evaluate_risks
from app.analytics.recommendation import generate_recommendation
from app.schemas.metric import PlayerMetricResponse


class AnalyticsEngine:
    """Deterministic, explainable analytics engine for ScoutLab player intelligence."""

    @classmethod
    def compute_player_intelligence(
        cls,
        player_id: int,
        recent_scores: List[float],
        recent_minutes: List[int],
        recent_starts: int,
        is_injured: bool = False,
        injury_kind: Optional[str] = None,
        injury_status: Optional[str] = None,
        is_suspended: bool = False,
        suspension_reason: Optional[str] = None,
        upcoming_fixture_diffs: Optional[List[int]] = None,
        upcoming_is_home: Optional[List[bool]] = None,
        current_price: Optional[float] = None,
        avg_30d_price: Optional[float] = None,
        price_change_7d: Optional[float] = 0.0,
    ) -> PlayerMetricResponse:
        """Compute all 6 core sub-scores, combined Scout Score, Starting XI, Risks, and Recommendation."""
        # 1. Sub-scores
        form_score = calculate_form_score(recent_scores)
        consistency_score = calculate_consistency_score(recent_scores)
        minutes_score = calculate_minutes_score(recent_minutes)
        fixture_score = calculate_fixture_score(upcoming_fixture_diffs or [3, 3, 3], upcoming_is_home)
        availability_score = calculate_availability_score(is_injured, injury_status, is_suspended)
        market_score = calculate_market_score(current_price, avg_30d_price)

        # 2. Composite Scout Score (0-100)
        scout_score = calculate_scout_score(
            form_score=form_score,
            consistency_score=consistency_score,
            minutes_score=minutes_score,
            fixture_score=fixture_score,
            availability_score=availability_score,
            market_score=market_score,
        )

        # 3. Starting XI Prediction (Deterministic)
        starting_pred = calculate_starting_probability(
            recent_starts=recent_starts,
            recent_appearances=len(recent_scores) if recent_scores else 5,
            recent_minutes=recent_minutes,
            is_injured=is_injured,
            injury_status=injury_status,
            is_suspended=is_suspended,
        )

        # 4. Multi-signal Risk Engine
        risk_score, risk_level, risk_factors = evaluate_risks(
            is_injured=is_injured,
            injury_kind=injury_kind,
            injury_status=injury_status,
            is_suspended=is_suspended,
            suspension_reason=suspension_reason,
            minutes_score=minutes_score,
            starting_prob=starting_pred.starting_probability,
            form_score=form_score,
            fixture_score=fixture_score,
            price_change_7d=price_change_7d,
        )

        # 5. Recommendation Engine
        rec_detail = generate_recommendation(
            scout_score=scout_score,
            form_score=form_score,
            minutes_score=minutes_score,
            fixture_score=fixture_score,
            availability_score=availability_score,
            market_score=market_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
        )

        return PlayerMetricResponse(
            player_id=player_id,
            form_score=form_score,
            consistency_score=consistency_score,
            minutes_score=minutes_score,
            fixture_score=fixture_score,
            market_score=market_score,
            availability_score=availability_score,
            scout_score=scout_score,
            risk_score=risk_score,
            risk_level=risk_level,
            starting_probability=starting_pred.starting_probability,
            recommendation=rec_detail.recommendation,
            confidence=rec_detail.confidence,
            calculated_at=datetime.now(timezone.utc),
            starting_prediction=starting_pred,
            recommendation_detail=rec_detail,
            risk_factors=risk_factors,
        )
