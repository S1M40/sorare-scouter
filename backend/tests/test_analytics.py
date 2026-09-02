import pytest
from app.analytics import (
    calculate_form_score,
    calculate_consistency_score,
    calculate_minutes_score,
    calculate_fixture_score,
    calculate_availability_score,
    calculate_market_score,
    calculate_scout_score,
    calculate_starting_probability,
    evaluate_risks,
    generate_recommendation,
    AnalyticsEngine,
)
from app.schemas.common import RecommendationEnum, RiskLevelEnum


def test_form_score_recency_weighting():
    # Empty scores should return neutral 50
    assert calculate_form_score([]) == 50.0

    # Recent high score vs older low score
    high_recent = calculate_form_score([90.0, 80.0, 70.0, 60.0, 50.0])
    low_recent = calculate_form_score([50.0, 60.0, 70.0, 80.0, 90.0])
    assert high_recent > low_recent
    assert 0 <= high_recent <= 100


def test_consistency_score_variance():
    # Identical scores should yield maximum consistency (~100)
    consistent = calculate_consistency_score([65.0, 65.0, 65.0, 65.0, 65.0])
    assert consistent >= 95.0

    # Highly erratic scores should yield low consistency
    erratic = calculate_consistency_score([10.0, 95.0, 20.0, 85.0, 15.0])
    assert erratic < consistent


def test_minutes_score():
    assert calculate_minutes_score([90, 90, 90]) == 100.0
    assert calculate_minutes_score([45, 45]) == 50.0
    assert calculate_minutes_score([0, 0]) == 0.0


def test_fixture_score():
    # Easy fixtures (difficulty 1) vs tough fixtures (difficulty 5)
    easy = calculate_fixture_score([1, 1, 1], is_home=[True, True, True])
    tough = calculate_fixture_score([5, 5, 5], is_home=[False, False, False])
    assert easy > tough
    assert easy >= 95.0
    assert tough <= 30.0


def test_availability_score():
    assert calculate_availability_score(is_injured=False, is_suspended=False) == 100.0
    assert calculate_availability_score(is_injured=True, injury_status="OUT") == 0.0
    assert calculate_availability_score(is_injured=True, injury_status="DOUBTFUL") == 40.0
    assert calculate_availability_score(is_suspended=True) == 0.0


def test_market_score():
    # Undervalued: price 70 EUR vs 100 EUR 30d baseline -> high buying score
    undervalued = calculate_market_score(current_price=70.0, avg_30d_price=100.0)
    # Inflated: price 150 EUR vs 100 EUR baseline -> low score
    inflated = calculate_market_score(current_price=150.0, avg_30d_price=100.0)
    assert undervalued > inflated
    assert undervalued >= 85.0


def test_scout_score_weights():
    # Balanced weights
    score = calculate_scout_score(
        form_score=80.0,
        consistency_score=80.0,
        minutes_score=80.0,
        fixture_score=80.0,
        availability_score=80.0,
        market_score=80.0,
    )
    assert score == 80.0

    # Availability dampener: if 0 availability, score is capped at 35
    injured_score = calculate_scout_score(
        form_score=95.0,
        consistency_score=90.0,
        minutes_score=90.0,
        fixture_score=90.0,
        availability_score=0.0,
        market_score=90.0,
    )
    assert injured_score <= 35.0


def test_starting_probability_prediction():
    pred = calculate_starting_probability(
        recent_starts=5,
        recent_appearances=5,
        recent_minutes=[90, 90, 90, 90, 90],
        is_injured=False,
        is_suspended=False,
    )
    assert pred.label == "PREDICTION"
    assert pred.starting_probability >= 85.0
    assert pred.expected_role == "Starter"

    # Suspended player should be 0%
    susp_pred = calculate_starting_probability(is_suspended=True)
    assert susp_pred.starting_probability == 0.0
    assert susp_pred.expected_role == "Out"


def test_risk_engine_and_recommendation():
    risk_score, risk_lvl, factors = evaluate_risks(
        is_injured=True,
        injury_kind="Hamstring Strain",
        injury_status="OUT",
        is_suspended=False,
    )
    assert risk_lvl == RiskLevelEnum.CRITICAL
    assert any("Hamstring" in f.message for f in factors)

    rec = generate_recommendation(
        scout_score=85.0,
        form_score=85.0,
        minutes_score=90.0,
        fixture_score=75.0,
        availability_score=100.0,
        market_score=80.0,
        risk_level=RiskLevelEnum.LOW,
        risk_factors=[],
    )
    assert rec.recommendation == RecommendationEnum.BUY
    assert len(rec.reasons) > 0


def test_analytics_engine_complete():
    intel = AnalyticsEngine.compute_player_intelligence(
        player_id=1,
        recent_scores=[75.0, 68.0, 82.0, 60.0, 71.0],
        recent_minutes=[90, 90, 90, 85, 90],
        recent_starts=5,
        current_price=50.0,
        avg_30d_price=60.0,
    )
    assert 0 <= intel.scout_score <= 100
    assert intel.starting_prediction.label == "PREDICTION"
    assert intel.recommendation in [r for r in RecommendationEnum]
