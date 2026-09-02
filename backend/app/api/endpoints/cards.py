from math import ceil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse, ApiListResponse, ApiPaginationMeta, ApiMeta
from app.schemas.card import CardWithPlayerResponse, CardPriceResponse, CardResponse
from app.services.card_service import CardService

router = APIRouter(prefix="/cards", tags=["Cards"])


@router.get("", response_model=ApiListResponse[CardWithPlayerResponse])
async def list_cards(
    player_id: Optional[int] = Query(None),
    rarity: Optional[str] = Query(None),
    season_year: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = CardService(db)
    cards, total = await service.get_cards(player_id, rarity, season_year, page, page_size)
    total_pages = ceil(total / page_size) if total > 0 else 1
    meta = ApiPaginationMeta(
        page=page, page_size=page_size, total=total, total_pages=total_pages, source="scoutlab"
    )
    return ApiListResponse(data=cards, meta=meta)


@router.get("/{card_id}", response_model=ApiResponse[CardWithPlayerResponse])
async def get_card(card_id: int, db: AsyncSession = Depends(get_db)):
    service = CardService(db)
    card = await service.get_card_by_id(card_id)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    return ApiResponse(data=card, meta=ApiMeta(source="scoutlab"))


@router.get("/{card_id}/prices", response_model=ApiResponse[List[CardPriceResponse]])
async def get_card_prices(
    card_id: int, limit: int = Query(30, ge=1, le=100), db: AsyncSession = Depends(get_db)
):
    service = CardService(db)
    prices = await service.get_card_prices(card_id, limit)
    return ApiResponse(data=prices, meta=ApiMeta(source="scoutlab"))
