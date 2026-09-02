from typing import List


def calculate_minutes_score(recent_minutes: List[int]) -> float:
    """Calculate Minutes Score (0-100) measuring recent playing time.
    
    A regular 90-minute starter receives near 100. Bench / sub players receive lower scores.
    """
    if not recent_minutes:
        return 50.0  # Unknown / unrated default

    sample = recent_minutes[:5]
    avg_minutes = sum(sample) / len(sample)
    
    # 90 minutes = 100%, clamped
    score = (avg_minutes / 90.0) * 100.0
    return round(max(0.0, min(100.0, score)), 1)
