from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.market_repository import MarketRepository
from app.schemas.market import (
    MarketMover,
    MarketOpportunity,
    TrendingCard,
    PlayerMarketOverview,
    MarketSummaryResponse,
)


class MarketService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = MarketRepository(session)

    async def get_market_summary(self) -> MarketSummaryResponse:
        return await self.repo.get_market_summary()

    async def get_movers(self, limit: int = 10) -> List[MarketMover]:
        return await self.repo.get_movers(limit)

    async def get_opportunities(self, limit: int = 10) -> List[MarketOpportunity]:
        return await self.repo.get_opportunities(limit)

    async def get_trending(self, limit: int = 10) -> List[TrendingCard]:
        return await self.repo.get_trending(limit)

    async def get_player_market(self, player_id: int) -> Optional[PlayerMarketOverview]:
        return await self.repo.get_player_market_overview(player_id)
