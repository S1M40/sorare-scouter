from typing import Optional


def calculate_market_score(current_price: Optional[float], avg_30d_price: Optional[float]) -> float:
    """Calculate Market Score (0-100) assessing market valuation opportunity.
    
    A price trading at a discount to its 30-day baseline yields a higher opportunity score.
    Overpriced / peaked cards yield a lower buying score.
    """
    if not current_price or not avg_30d_price or avg_30d_price <= 0:
        return 50.0  # Neutral baseline

    # Price ratio: current / baseline
    ratio = current_price / avg_30d_price

    if ratio <= 0.70:
        # Deep 30%+ discount -> High score 90-98
        score = 95.0
    elif ratio < 1.0:
        # 0.70 to 1.0 -> 70 to 90
        discount = (1.0 - ratio) / 0.30
        score = 70.0 + (discount * 20.0)
    elif ratio == 1.0:
        score = 60.0
    elif ratio <= 1.30:
        # Premium 1.0 to 1.30 -> 40 to 60
        premium = (ratio - 1.0) / 0.30
        score = 60.0 - (premium * 20.0)
    else:
        # Heavily inflated > 30% premium -> 20 to 35
        score = max(15.0, 40.0 - ((ratio - 1.30) * 20.0))

    return round(max(0.0, min(100.0, score)), 1)
