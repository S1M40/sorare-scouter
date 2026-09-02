import math
from typing import List


def calculate_consistency_score(scores: List[float]) -> float:
    """Calculate Consistency Score (0-100) based on score variance.
    
    A player whose scores deviate minimally around their mean is rewarded
    with a higher consistency score.
    """
    if not scores or len(scores) < 2:
        return 50.0  # Default neutral

    # Take up to last 15 scores
    sample = scores[:15]
    mean = sum(sample) / len(sample)
    variance = sum((x - mean) ** 2 for x in sample) / len(sample)
    std_dev = math.sqrt(variance)

    # In Sorare scoring (0-100 scale), standard deviation typically ranges from 5 to 30.
    # std_dev <= 5 gives ~95-100 score, std_dev >= 30 gives ~25-30 score.
    # Linear dampening formula:
    score = 100.0 - (std_dev * 2.5)
    return round(max(0.0, min(100.0, score)), 1)
