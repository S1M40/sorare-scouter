from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, func, desc, asc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models.fixture import SO5Fixture
from app.models.game import Game
from app.repositories.base import BaseRepository


class FixtureRepository(BaseRepository[SO5Fixture]):
    def __init__(self, session: AsyncSession):
        super().__init__(SO5Fixture, session)

    async def get_so5_fixtures(
        self, state: Optional[str] = None, limit: int = 20
    ) -> List[SO5Fixture]:
        query = select(SO5Fixture)
        if state:
            query = query.where(SO5Fixture.state == state)
        query = query.order_by(asc(SO5Fixture.start_date)).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_current_gameweek(self) -> Optional[SO5Fixture]:
        """Fetch current open or live gameweek, or next upcoming."""
        query = (
            select(SO5Fixture)
            .where(SO5Fixture.state.in_(["opened", "live"]))
            .order_by(asc(SO5Fixture.start_date))
        )
        result = await self.session.execute(query)
        fixture = result.scalars().first()
        if not fixture:
            # Fallback to earliest upcoming
            next_q = (
                select(SO5Fixture)
                .where(SO5Fixture.state == "upcoming")
                .order_by(asc(SO5Fixture.start_date))
            )
            next_res = await self.session.execute(next_q)
            fixture = next_res.scalars().first()
        return fixture

    async def get_games(
        self,
        competition_id: Optional[int] = None,
        club_id: Optional[int] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> Tuple[List[Game], int]:
        query = (
            select(Game)
            .options(
                joinedload(Game.home_club),
                joinedload(Game.away_club),
                joinedload(Game.competition),
            )
        )

        if competition_id:
            query = query.where(Game.competition_id == competition_id)
        if club_id:
            query = query.where(
                or_(Game.home_club_id == club_id, Game.away_club_id == club_id)
            )
        if status:
            query = query.where(Game.status == status)
        if date_from:
            query = query.where(Game.date >= date_from)
        if date_to:
            query = query.where(Game.date <= date_to)

        count_subquery = query.with_only_columns(func.count(Game.id)).order_by(None)
        total_res = await self.session.execute(count_subquery)
        total = total_res.scalar() or 0

        query = query.order_by(asc(Game.date)).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_game_by_id(self, game_id: int) -> Optional[Game]:
        query = (
            select(Game)
            .where(Game.id == game_id)
            .options(
                joinedload(Game.home_club),
                joinedload(Game.away_club),
                joinedload(Game.competition),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()
