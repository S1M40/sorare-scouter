from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.watchlist_repository import WatchlistRepository
from app.schemas.watchlist import WatchlistResponse, WatchlistCreate
from app.services.player_service import PlayerService


class WatchlistService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = WatchlistRepository(session)
        self.player_service = PlayerService(session)

    async def get_watchlist(self, user_id: int) -> List[WatchlistResponse]:
        items = await self.repo.get_user_watchlist(user_id)
        responses = []
        for it in items:
            p_item = self.player_service._to_list_item(it.player) if it.player else None
            responses.append(
                WatchlistResponse(
                    id=it.id,
                    user_id=it.user_id,
                    player_id=it.player_id,
                    target_price=it.target_price,
                    notes=it.notes,
                    created_at=it.created_at,
                    player=p_item,
                )
            )
        return responses

    async def add_to_watchlist(
        self, user_id: int, player_id: int, payload: Optional[WatchlistCreate] = None
    ) -> WatchlistResponse:
        target_price = payload.target_price if payload else None
        notes = payload.notes if payload else None
        item = await self.repo.add_to_watchlist(user_id, player_id, target_price, notes)
        return WatchlistResponse.model_validate(item)

    async def remove_from_watchlist(self, user_id: int, player_id: int) -> bool:
        return await self.repo.remove_from_watchlist(user_id, player_id)
