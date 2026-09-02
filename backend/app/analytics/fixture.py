from typing import List, Optional


def calculate_fixture_score(upcoming_difficulties: List[int], is_home: Optional[List[bool]] = None) -> float:
    """Calculate Fixture Score (0-100) evaluating upcoming match difficulty.
    
    Difficulty rating per match is 1 (easiest) to 5 (toughest).
    A schedule with rating 1 gives high fixture score (~90-100).
    A schedule with rating 5 gives low fixture score (~20-30).
    Home matches give a +5 point bonus.
    """
    if not upcoming_difficulties:
        return 50.0  # Neutral fixture run

    sample_diffs = upcoming_difficulties[:3]
    sample_homes = is_home[:3] if is_home else [False] * len(sample_diffs)

    scores = []
    for diff, home in zip(sample_diffs, sample_homes):
        # 1 -> 100, 2 -> 80, 3 -> 60, 4 -> 40, 5 -> 20
        match_score = 120.0 - (diff * 20.0)
        if home:
            match_score += 5.0
        scores.append(match_score)

    avg_score = sum(scores) / len(scores)
    return round(max(0.0, min(100.0, avg_score)), 1)
