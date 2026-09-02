from typing import Optional


def calculate_availability_score(
    is_injured: bool = False,
    injury_status: Optional[str] = None,
    is_suspended: bool = False,
) -> float:
    """Calculate Availability Score (0-100) accounting for injury and suspension statuses.
    
    100 = Fully fit and available.
    0 = Confirmed OUT or suspended.
    """
    if is_suspended:
        return 0.0

    if not is_injured or not injury_status:
        return 100.0

    status = injury_status.upper()
    if status == "OUT":
        return 0.0
    elif status == "DOUBTFUL":
        return 40.0
    elif status in {"RECOVERING", "QUESTIONABLE"}:
        return 65.0
    elif status in {"PROBABLE", "MINOR"}:
        return 85.0

    return 50.0
