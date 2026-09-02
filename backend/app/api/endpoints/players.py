from math import ceil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse, ApiListResponse, ApiPaginationMeta, ApiMeta
from app.schemas.player import (
    PlayerListItemResponse,
    PlayerDetailResponse,
    PlayerFilterParams,
)
from app.schemas.score import PlayerGameScoreResponse
from app.schemas.fixture import GameResponse
from app.schemas.market import PlayerMarketOverview
from app.schemas.news import NewsResponse
from app.schemas.metric import PlayerMetricResponse
from app.services.player_service import PlayerService
from app.services.market_service import MarketService

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("", response_model=ApiListResponse[PlayerListItemResponse])
async def list_players(
    search: Optional[str] = Query(None, description="Search by player or club name"),
    position: Optional[str] = Query(None, description="Goalkeeper, Defender, Midfielder, Forward"),
    club: Optional[str] = Query(None, description="Club name or slug"),
    competition: Optional[str] = Query(None, description="Competition name or slug"),
    age_min: Optional[int] = Query(None, ge=15, le=45),
    age_max: Optional[int] = Query(None, ge=15, le=45),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    score_min: Optional[float] = Query(None, ge=0, le=100),
    score_max: Optional[float] = Query(None, ge=0, le=100),
    form_min: Optional[float] = Query(None, ge=0, le=100),
    starting_probability_min: Optional[float] = Query(None, ge=0, le=100),
    injury_status: Optional[str] = Query(None, description="all, fit, injured, suspended"),
    recommendation: Optional[str] = Query(None, description="BUY, WATCH, HOLD, SELL, AVOID"),
    sort_by: Optional[str] = Query("scout_score", description="scout_score, form_score, starting_probability, age, name"),
    sort_order: Optional[str] = Query("desc", description="asc, desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List players with multi-field filters, scout score ordering, and pagination."""
    params = PlayerFilterParams(
        search=search,
        position=position,
        club=club,
        competition=competition,
        age_min=age_min,
        age_max=age_max,
        price_min=price_min,
        price_max=price_max,
        score_min=score_min,
        score_max=score_max,
        form_min=form_min,
        starting_probability_min=starting_probability_min,
        injury_status=injury_status,
        recommendation=recommendation,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    service = PlayerService(db)
    items, total = await service.get_players(params)

    total_pages = ceil(total / page_size) if total > 0 else 1
    meta = ApiPaginationMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        source="scoutlab",
    )
    return ApiListResponse(data=items, meta=meta)


@router.get("/{player_id}", response_model=ApiResponse[PlayerDetailResponse])
async def get_player_profile(player_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve full player profile with club, cards, active injuries, and recent match scores."""
    service = PlayerService(db)
    player = await service.get_player_profile(player_id)
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return ApiResponse(data=player, meta=ApiMeta(source="scoutlab"))


@router.get("/{player_id}/scores", response_model=ApiResponse[List[PlayerGameScoreResponse]])
async def get_player_scores(
    player_id: int, limit: int = Query(15, ge=1, le=50), db: AsyncSession = Depends(get_db)
):
    """Retrieve match score history for player."""
    service = PlayerService(db)
    scores = await service.get_player_scores(player_id, limit)
    return ApiResponse(data=scores, meta=ApiMeta(source="scoutlab"))


@router.get("/{player_id}/fixtures", response_model=ApiResponse[List[GameResponse]])
async def get_player_fixtures(
    player_id: int, limit: int = Query(5, ge=1, le=20), db: AsyncSession = Depends(get_db)
):
    """Retrieve upcoming club fixtures for player."""
    service = PlayerService(db)
    fixtures = await service.get_player_fixtures(player_id, limit)
    return ApiResponse(data=fixtures, meta=ApiMeta(source="scoutlab"))


@router.get("/{player_id}/market", response_model=ApiResponse[PlayerMarketOverview])
async def get_player_market(player_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve player market pricing metrics, floor price, and valuation trends."""
    service = MarketService(db)
    market_overview = await service.get_player_market(player_id)
    if not market_overview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market data not found for player")
    return ApiResponse(data=market_overview, meta=ApiMeta(source="scoutlab"))


@router.get("/{player_id}/news", response_model=ApiResponse[List[NewsResponse]])
async def get_player_news(
    player_id: int, limit: int = Query(10, ge=1, le=30), db: AsyncSession = Depends(get_db)
):
    """Retrieve recent news reports linked to player."""
    service = PlayerService(db)
    news = await service.get_player_news(player_id, limit)
    return ApiResponse(data=news, meta=ApiMeta(source="scoutlab"))


@router.get("/{player_id}/metrics", response_model=ApiResponse[PlayerMetricResponse])
async def get_player_metrics(player_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve detailed explainable intelligence metrics: Scout Score, Starting XI Prediction, and Risk Factors."""
    service = PlayerService(db)
    player = await service.get_player_profile(player_id)
    if not player or not player.metric:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metrics not found for player")
    return ApiResponse(data=player.metric, meta=ApiMeta(source="scoutlab"))
