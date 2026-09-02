from typing import List, Optional
from app.schemas.metric import StartingXIPrediction


def calculate_starting_probability(
    recent_starts: int = 5,
    recent_appearances: int = 5,
    recent_minutes: Optional[List[int]] = None,
    is_injured: bool = False,
    injury_status: Optional[str] = None,
    is_suspended: bool = False,
    days_since_last_match: Optional[int] = 4,
) -> StartingXIPrediction:
    """Calculate deterministic starting XI probability (0-100%).
    
    Clearly tagged as 'PREDICTION'. Evaluates recent starting consistency,
    injury/suspension availability, and rotation risk factors.
    """
    factors: List[str] = []

    # 1. Suspensions and Injuries override
    if is_suspended:
        return StartingXIPrediction(
            starting_probability=0.0,
            label="PREDICTION",
            confidence=95.0,
            expected_role="Out",
            factors=["Player is serving an active suspension."],
        )

    if is_injured:
        status = (injury_status or "OUT").upper()
        if status == "OUT":
            return StartingXIPrediction(
                starting_probability=0.0,
                label="PREDICTION",
                confidence=92.0,
                expected_role="Out",
                factors=["Confirmed active injury."],
            )
        elif status == "DOUBTFUL":
            return StartingXIPrediction(
                starting_probability=25.0,
                label="PREDICTION",
                confidence=75.0,
                expected_role="Bench",
                factors=["Player marked as doubtful due to injury."],
            )
        elif status in {"QUESTIONABLE", "RECOVERING"}:
            return StartingXIPrediction(
                starting_probability=50.0,
                label="PREDICTION",
                confidence=70.0,
                expected_role="Rotation",
                factors=["Returning from injury, partial minutes expected."],
            )

    # 2. Historical starts & minutes
    minutes_list = recent_minutes or [90] * recent_starts
    avg_minutes = (sum(minutes_list) / len(minutes_list)) if minutes_list else 90.0

    base_prob = 50.0

    # Start ratio (e.g. 5/5 -> +30, 4/5 -> +20, 1/5 -> -20)
    if recent_appearances > 0:
        start_ratio = recent_starts / recent_appearances
        if start_ratio >= 0.8:
            base_prob += 35.0
            factors.append(f"Started {recent_starts} of last {recent_appearances} matches.")
        elif start_ratio >= 0.6:
            base_prob += 20.0
            factors.append(f"Regular starter ({recent_starts}/{recent_appearances} starts).")
        elif start_ratio >= 0.4:
            base_prob += 5.0
            factors.append("Frequent rotation candidate.")
        else:
            base_prob -= 20.0
            factors.append("Primarily used as substitute.")

    # Minutes factor
    if avg_minutes >= 80:
        base_prob += 10.0
        factors.append("Averaging 80+ minutes per appearance.")
    elif avg_minutes < 45:
        base_prob -= 15.0
        factors.append("Limited match minutes recently.")

    # Congestion / rotation factor
    if days_since_last_match is not None and days_since_last_match <= 3:
        base_prob -= 8.0
        factors.append("Short rest period (< 4 days), minor rotation chance.")

    final_prob = round(max(5.0, min(95.0, base_prob)), 1)

    if final_prob >= 75.0:
        role = "Starter"
    elif final_prob >= 45.0:
        role = "Rotation"
    else:
        role = "Bench"

    confidence = 85.0 if recent_appearances >= 5 else 65.0

    return StartingXIPrediction(
        starting_probability=final_prob,
        label="PREDICTION",
        confidence=confidence,
        expected_role=role,
        factors=factors,
    )
