from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.fixture_repository import FixtureRepository
from app.schemas.fixture import GameResponse, SO5FixtureResponse


class FixtureService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = FixtureRepository(session)

    async def get_so5_fixtures(self, state: Optional[str] = None) -> List[SO5FixtureResponse]:
        fixtures = await self.repo.get_so5_fixtures(state)
        return [SO5FixtureResponse.model_validate(f) for f in fixtures]

    async def get_current_gameweek(self) -> Optional[SO5FixtureResponse]:
        gw = await self.repo.get_current_gameweek()
        if not gw:
            return None
        return SO5FixtureResponse.model_validate(gw)

    async def get_games(
        self,
        competition_id: Optional[int] = None,
        club_id: Optional[int] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> Tuple[List[GameResponse], int]:
        games, total = await self.repo.get_games(
            competition_id, club_id, status, date_from, date_to, page, page_size
        )
        return [GameResponse.model_validate(g) for g in games], total

    async def get_game_by_id(self, game_id: int) -> Optional[GameResponse]:
        g = await self.repo.get_game_by_id(game_id)
        if not g:
            return None
        return GameResponse.model_validate(g)
