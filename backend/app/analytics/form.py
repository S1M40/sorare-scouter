from typing import List


def calculate_form_score(scores: List[float]) -> float:
    """Calculate normalized Form Score (0-100) based on recent match scores.
    
    Uses exponential / recency weighting over up to the last 5 appearances.
    """
    if not scores:
        return 50.0  # Default neutral form for unrated/new players

    recent = scores[:5]
    n = len(recent)

    # Weights prioritizing most recent matches
    weights_pool = [0.35, 0.25, 0.20, 0.12, 0.08]
    weights = weights_pool[:n]
    total_weight = sum(weights)
    norm_weights = [w / total_weight for w in weights]

    weighted_score = sum(score * weight for score, weight in zip(recent, norm_weights))
    
    # Clamp to 0.0 - 100.0
    return round(max(0.0, min(100.0, weighted_score)), 1)
