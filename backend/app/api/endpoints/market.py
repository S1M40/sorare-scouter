from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse, ApiMeta
from app.schemas.market import (
    MarketMover,
    MarketOpportunity,
    TrendingCard,
    PlayerMarketOverview,
    MarketSummaryResponse,
)
from app.services.market_service import MarketService

router = APIRouter(prefix="/market", tags=["Market"])


@router.get("", response_model=ApiResponse[MarketSummaryResponse])
async def get_market_overview(db: AsyncSession = Depends(get_db)):
    """Retrieve full market intelligence summary including volume, movers, and opportunities."""
    service = MarketService(db)
    summary = await service.get_market_summary()
    return ApiResponse(data=summary, meta=ApiMeta(source="scoutlab"))


@router.get("/movers", response_model=ApiResponse[List[MarketMover]])
async def get_market_movers(
    limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)
):
    """Retrieve top percentage gainers and losers in secondary market prices."""
    service = MarketService(db)
    movers = await service.get_movers(limit)
    return ApiResponse(data=movers, meta=ApiMeta(source="scoutlab"))


@router.get("/opportunities", response_model=ApiResponse[List[MarketOpportunity]])
async def get_market_opportunities(
    limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)
):
    """Retrieve top scouting purchase opportunities trading below 30-day fair valuation."""
    service = MarketService(db)
    opps = await service.get_opportunities(limit)
    return ApiResponse(data=opps, meta=ApiMeta(source="scoutlab"))


@router.get("/trending", response_model=ApiResponse[List[TrendingCard]])
async def get_trending_cards(
    limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)
):
    """Retrieve cards with highest trading frequency and 24h volume."""
    service = MarketService(db)
    trending = await service.get_trending(limit)
    return ApiResponse(data=trending, meta=ApiMeta(source="scoutlab"))


@router.get("/{player_id}", response_model=ApiResponse[PlayerMarketOverview])
async def get_player_market_detail(player_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve historical market prices and card inventory for a player."""
    service = MarketService(db)
    overview = await service.get_player_market(player_id)
    if not overview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return ApiResponse(data=overview, meta=ApiMeta(source="scoutlab"))
