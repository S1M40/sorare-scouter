from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from app.database import get_db
from app.api.deps import get_optional_current_user
from app.models import Card, CardPrice, Player, PlayerMetric, Injury
from app.schemas.common import ApiResponse, ApiMeta
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


class PortfolioSummaryResponse(BaseModel):
    total_value: float = 0.0
    change_7d: float = 0.0
    change_pct_7d: float = 0.0
    average_score: float = 0.0
    card_count: int = 0
    at_risk: int = 0


@router.get("/summary", response_model=ApiResponse[PortfolioSummaryResponse])
async def get_portfolio_summary(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    """Get portfolio summary for the current user."""
    # Get all cards with their latest prices and player info
    result = await db.execute(
        select(Card)
        .options(
            selectinload(Card.prices),
            joinedload(Card.player).joinedload(Player.metric),
            joinedload(Card.player).selectinload(Player.injuries),
        )
    )
    cards = result.unique().scalars().all()

    if not cards:
        return ApiResponse(
            data=PortfolioSummaryResponse(),
            meta=ApiMeta(source="scoutlab"),
        )

    total_value = 0.0
    total_acquired = 0.0
    total_score = 0.0
    at_risk = 0
    scored_count = 0

    for card in cards:
        # Use latest price from relations
        latest_price = 0.0
        if card.prices:
            prices_sorted = sorted(card.prices, key=lambda p: p.observed_at, reverse=True)
            latest_price = prices_sorted[0].price
        
        total_value += latest_price
        
        if card.prices:
            prices_asc = sorted(card.prices, key=lambda p: p.observed_at)
            total_acquired += prices_asc[0].price
        else:
            total_acquired += latest_price
        
        # Player stats
        if card.player:
            if card.player.metric:
                total_score += card.player.metric.form_score
                scored_count += 1
            # Check at-risk (active injuries)
            active_injuries = [i for i in (card.player.injuries or []) if i.active]
            if active_injuries:
                at_risk += 1

    change_7d = round(total_value - total_acquired, 2)
    change_pct_7d = round((change_7d / total_acquired * 100) if total_acquired > 0 else 0.0, 1)
    avg_score = round(total_score / scored_count, 1) if scored_count > 0 else 0.0

    return ApiResponse(
        data=PortfolioSummaryResponse(
            total_value=round(total_value, 2),
            change_7d=change_7d,
            change_pct_7d=change_pct_7d,
            average_score=avg_score,
            card_count=len(cards),
            at_risk=at_risk,
        ),
        meta=ApiMeta(source="scoutlab"),
    )
