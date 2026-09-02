from typing import List, Optional, Tuple
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from app.models.card import Card, CardPrice
from app.models.player import Player
from app.repositories.base import BaseRepository


class CardRepository(BaseRepository[Card]):
    def __init__(self, session: AsyncSession):
        super().__init__(Card, session)

    async def get_cards(
        self,
        player_id: Optional[int] = None,
        rarity: Optional[str] = None,
        season_year: Optional[int] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> Tuple[List[Card], int]:
        query = select(Card).options(
            selectinload(Card.prices),
            joinedload(Card.player).joinedload(Player.club)
        )

        if player_id:
            query = query.where(Card.player_id == player_id)
        if rarity:
            query = query.where(Card.rarity == rarity)
        if season_year:
            query = query.where(Card.season_year == season_year)

        count_subquery = query.with_only_columns(func.count(Card.id)).order_by(None)
        total_res = await self.session.execute(count_subquery)
        total = total_res.scalar() or 0

        query = query.order_by(desc(Card.id)).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_card_prices(self, card_id: int, limit: int = 30) -> List[CardPrice]:
        query = (
            select(CardPrice)
            .where(CardPrice.card_id == card_id)
            .order_by(desc(CardPrice.observed_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
