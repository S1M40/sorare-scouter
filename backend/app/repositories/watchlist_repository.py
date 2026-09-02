from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from app.models.watchlist import Watchlist
from app.models.player import Player
from app.models.card import Card
from app.repositories.base import BaseRepository


class WatchlistRepository(BaseRepository[Watchlist]):
    def __init__(self, session: AsyncSession):
        super().__init__(Watchlist, session)

    async def get_user_watchlist(self, user_id: int) -> List[Watchlist]:
        query = (
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .options(
                joinedload(Watchlist.player)
                .joinedload(Player.club),
                joinedload(Watchlist.player)
                .joinedload(Player.metric),
                joinedload(Watchlist.player)
                .selectinload(Player.cards).selectinload(Card.prices),
            )
            .order_by(Watchlist.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_to_watchlist(
        self, user_id: int, player_id: int, target_price: Optional[float] = None, notes: Optional[str] = None
    ) -> Watchlist:
        # Check existing
        query = select(Watchlist).where(
            Watchlist.user_id == user_id, Watchlist.player_id == player_id
        )
        res = await self.session.execute(query)
        existing = res.scalars().first()
        if existing:
            if target_price is not None:
                existing.target_price = target_price
            if notes is not None:
                existing.notes = notes
            return existing

        item = Watchlist(
            user_id=user_id,
            player_id=player_id,
            target_price=target_price,
            notes=notes,
        )
        self.session.add(item)
        await self.session.flush()
        # Re-fetch with player eagerly loaded so Pydantic model_validate works
        query = (
            select(Watchlist)
            .where(Watchlist.id == item.id)
            .options(joinedload(Watchlist.player))
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def remove_from_watchlist(self, user_id: int, player_id: int) -> bool:
        stmt = delete(Watchlist).where(
            Watchlist.user_id == user_id, Watchlist.player_id == player_id
        )
        res = await self.session.execute(stmt)
        return res.rowcount > 0
