from typing import Optional
from app.config import settings


def calculate_scout_score(
    form_score: float,
    consistency_score: float,
    minutes_score: float,
    fixture_score: float,
    availability_score: float,
    market_score: float,
    w_form: Optional[float] = None,
    w_consistency: Optional[float] = None,
    w_minutes: Optional[float] = None,
    w_fixture: Optional[float] = None,
    w_availability: Optional[float] = None,
    w_market: Optional[float] = None,
) -> float:
    """Calculate the comprehensive normalized 0-100 Scout Score.
    
    Weights are configurable dynamically and never hardcoded in the core calculation.
    """
    wf = w_form if w_form is not None else settings.FORM_WEIGHT
    wc = w_consistency if w_consistency is not None else settings.CONSISTENCY_WEIGHT
    wm = w_minutes if w_minutes is not None else settings.MINUTES_WEIGHT
    wfx = w_fixture if w_fixture is not None else settings.FIXTURE_WEIGHT
    wa = w_availability if w_availability is not None else settings.AVAILABILITY_WEIGHT
    wmkt = w_market if w_market is not None else settings.MARKET_WEIGHT

    total_weight = wf + wc + wm + wfx + wa + wmkt
    if total_weight <= 0:
        total_weight = 1.0

    weighted_sum = (
        (form_score * wf)
        + (consistency_score * wc)
        + (minutes_score * wm)
        + (fixture_score * wfx)
        + (availability_score * wa)
        + (market_score * wmkt)
    )

    final_score = weighted_sum / total_weight

    # Availability dampener: If player is unavailable (0 availability), cap scout score to max 35
    if availability_score == 0:
        final_score = min(final_score, 35.0)

    return round(max(0.0, min(100.0, final_score)), 1)
