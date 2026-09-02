from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse, ApiMeta
from app.schemas.watchlist import WatchlistResponse, WatchlistCreate
from app.services.watchlist_service import WatchlistService

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.get("", response_model=ApiResponse[List[WatchlistResponse]])
async def get_watchlist(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WatchlistService(db)
    items = await service.get_watchlist(user_id=current_user.id)
    return ApiResponse(data=items, meta=ApiMeta(source="scoutlab"))


@router.post("/{player_id}", response_model=ApiResponse[WatchlistResponse])
async def add_to_watchlist(
    player_id: int,
    payload: Optional[WatchlistCreate] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WatchlistService(db)
    item = await service.add_to_watchlist(
        user_id=current_user.id, player_id=player_id, payload=payload
    )
    return ApiResponse(data=item, meta=ApiMeta(source="scoutlab"))


@router.delete("/{player_id}", response_model=ApiResponse[dict])
async def remove_from_watchlist(
    player_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WatchlistService(db)
    removed = await service.remove_from_watchlist(user_id=current_user.id, player_id=player_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not in watchlist")
    return ApiResponse(data={"success": True, "player_id": player_id}, meta=ApiMeta(source="scoutlab"))
