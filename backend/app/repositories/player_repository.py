from typing import List, Optional, Tuple
from sqlalchemy import select, func, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from app.models.player import Player
from app.models.club import Club
from app.models.competition import Competition
from app.models.metric import PlayerMetric
from app.models.injury import Injury
from app.models.suspension import Suspension
from app.models.card import Card, CardPrice
from app.models.score import PlayerGameScore
from app.models.game import Game
from app.models.news import News, NewsPlayerLink
from app.schemas.player import PlayerFilterParams
from app.repositories.base import BaseRepository


class PlayerRepository(BaseRepository[Player]):
    def __init__(self, session: AsyncSession):
        super().__init__(Player, session)

    async def get_players_filtered(
        self, params: PlayerFilterParams
    ) -> Tuple[List[Player], int]:
        """Query players with multi-field filtering, metric joins, sorting, and pagination."""
        query = (
            select(Player)
            .outerjoin(Player.club)
            .outerjoin(Player.metric)
            .options(
                joinedload(Player.club),
                joinedload(Player.metric),
                selectinload(Player.injuries),
                selectinload(Player.suspensions),
                selectinload(Player.cards).selectinload(Card.prices),
            )
        )

        # Apply filters
        if params.search:
            pattern = f"%{params.search.strip()}%"
            query = query.where(
                or_(
                    Player.display_name.ilike(pattern),
                    Player.first_name.ilike(pattern),
                    Player.last_name.ilike(pattern),
                    Club.name.ilike(pattern),
                )
            )

        if params.position:
            query = query.where(Player.position.ilike(params.position))

        if params.club:
            query = query.where(
                or_(Club.name.ilike(f"%{params.club}%"), Club.slug == params.club)
            )

        if params.competition:
            query = query.outerjoin(Club.competition).where(
                or_(Competition.name.ilike(f"%{params.competition}%"), Competition.slug == params.competition)
            )

        if params.age_min is not None:
            query = query.where(Player.age >= params.age_min)

        if params.age_max is not None:
            query = query.where(Player.age <= params.age_max)

        if params.form_min is not None:
            query = query.where(PlayerMetric.form_score >= params.form_min)

        if params.score_min is not None:
            query = query.where(PlayerMetric.scout_score >= params.score_min)

        if params.score_max is not None:
            query = query.where(PlayerMetric.scout_score <= params.score_max)

        if params.starting_probability_min is not None:
            query = query.where(
                PlayerMetric.starting_probability >= params.starting_probability_min
            )

        if params.recommendation:
            query = query.where(
                PlayerMetric.recommendation.ilike(params.recommendation)
            )

        # Injury / Suspension status filter
        if params.injury_status:
            status_lower = params.injury_status.lower()
            if status_lower == "fit":
                query = query.where(PlayerMetric.availability_score >= 80.0)
            elif status_lower == "injured":
                query = query.where(
                    Player.id.in_(
                        select(Injury.player_id).where(Injury.active == True)
                    )
                )
            elif status_lower == "suspended":
                query = query.where(
                    Player.id.in_(
                        select(Suspension.player_id).where(Suspension.active == True)
                    )
                )

        # Count total matching rows
        count_subquery = query.with_only_columns(func.count(Player.id)).order_by(None)
        total_count_res = await self.session.execute(count_subquery)
        total_count = total_count_res.scalar() or 0

        # Sorting
        sort_col = PlayerMetric.scout_score
        if params.sort_by == "form_score":
            sort_col = PlayerMetric.form_score
        elif params.sort_by == "starting_probability":
            sort_col = PlayerMetric.starting_probability
        elif params.sort_by == "age":
            sort_col = Player.age
        elif params.sort_by == "name":
            sort_col = Player.display_name

        if params.sort_order == "asc":
            query = query.order_by(asc(sort_col), asc(Player.id))
        else:
            query = query.order_by(desc(sort_col), desc(Player.id))

        # Pagination
        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)

        result = await self.session.execute(query)
        players = list(result.unique().scalars().all())
        return players, total_count

    async def get_player_full_profile(self, player_id: int) -> Optional[Player]:
        """Fetch player with all sub-relations eagerly loaded."""
        query = (
            select(Player)
            .where(Player.id == player_id)
            .options(
                joinedload(Player.club),
                joinedload(Player.metric),
                selectinload(Player.injuries),
                selectinload(Player.suspensions),
                selectinload(Player.scores).joinedload(PlayerGameScore.game),
                selectinload(Player.cards).selectinload(Card.prices),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_player_scores(self, player_id: int, limit: int = 15) -> List[PlayerGameScore]:
        """Get recent game scores for player."""
        query = (
            select(PlayerGameScore)
            .where(PlayerGameScore.player_id == player_id)
            .join(PlayerGameScore.game)
            .order_by(desc(Game.date))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_player_fixtures(self, player_id: int, limit: int = 5) -> List[Game]:
        """Get upcoming fixtures for player's club."""
        player = await self.get_by_id(player_id)
        if not player or not player.active_club_id:
            return []

        club_id = player.active_club_id
        query = (
            select(Game)
            .where(
                or_(Game.home_club_id == club_id, Game.away_club_id == club_id),
                Game.status.in_(["SCHEDULED", "LIVE"]),
            )
            .options(
                joinedload(Game.home_club),
                joinedload(Game.away_club),
                joinedload(Game.competition),
            )
            .order_by(asc(Game.date))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_player_news(self, player_id: int, limit: int = 10) -> List[News]:
        """Get news articles linked to a player."""
        query = (
            select(News)
            .join(NewsPlayerLink, News.id == NewsPlayerLink.news_id)
            .where(NewsPlayerLink.player_id == player_id)
            .order_by(desc(News.published_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
