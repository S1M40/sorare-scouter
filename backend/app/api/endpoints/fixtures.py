from datetime import datetime
from math import ceil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse, ApiListResponse, ApiPaginationMeta, ApiMeta
from app.schemas.fixture import GameResponse, SO5FixtureResponse
from app.services.fixture_service import FixtureService

router = APIRouter(prefix="/fixtures", tags=["Fixtures"])


@router.get("", response_model=ApiListResponse[GameResponse])
async def list_fixtures(
    competition_id: Optional[int] = Query(None),
    club_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = FixtureService(db)
    games, total = await service.get_games(
        competition_id, club_id, status, date_from, date_to, page, page_size
    )
    total_pages = ceil(total / page_size) if total > 0 else 1
    meta = ApiPaginationMeta(
        page=page, page_size=page_size, total=total, total_pages=total_pages, source="scoutlab"
    )
    return ApiListResponse(data=games, meta=meta)


@router.get("/gameweeks", response_model=ApiResponse[List[SO5FixtureResponse]])
async def list_gameweeks(
    state: Optional[str] = Query(None, description="upcoming, opened, live, closed"),
    db: AsyncSession = Depends(get_db),
):
    service = FixtureService(db)
    gameweeks = await service.get_so5_fixtures(state)
    return ApiResponse(data=gameweeks, meta=ApiMeta(source="scoutlab"))


@router.get("/{fixture_id}", response_model=ApiResponse[GameResponse])
async def get_fixture(fixture_id: int, db: AsyncSession = Depends(get_db)):
    service = FixtureService(db)
    game = await service.get_game_by_id(fixture_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixture not found")
    return ApiResponse(data=game, meta=ApiMeta(source="scoutlab"))
