from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.player_repository import PlayerRepository
from app.schemas.player import (
    PlayerListItemResponse,
    PlayerDetailResponse,
    PlayerFilterParams,
)
from app.schemas.score import PlayerGameScoreResponse
from app.schemas.fixture import GameResponse
from app.schemas.card import CardResponse
from app.schemas.news import NewsResponse
from app.schemas.metric import PlayerMetricResponse
from app.models.player import Player
from app.analytics.engine import AnalyticsEngine


class PlayerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PlayerRepository(session)

    def _to_list_item(self, p: Player) -> PlayerListItemResponse:
        curr_price = None
        if p.cards and p.cards[0].prices:
            curr_price = p.cards[0].prices[0].price
        elif p.price_snapshots:
            curr_price = p.price_snapshots[0].average_price

        is_injured = any(inj.active for inj in p.injuries)
        is_suspended = any(susp.active for susp in p.suspensions)

        metric = p.metric
        return PlayerListItemResponse(
            id=p.id,
            sorare_id=p.sorare_id,
            slug=p.slug,
            display_name=p.display_name,
            first_name=p.first_name,
            last_name=p.last_name,
            age=p.age,
            position=p.position,
            nationality=p.nationality,
            image_url=p.image_url,
            club=p.club,
            scout_score=metric.scout_score if metric else 50.0,
            form_score=metric.form_score if metric else 50.0,
            starting_probability=metric.starting_probability if metric else 50.0,
            recommendation=metric.recommendation if metric else "HOLD",
            risk_level=metric.risk_level if metric else "LOW",
            current_floor_price=curr_price,
            currency="EUR",
            is_injured=is_injured,
            is_suspended=is_suspended,
        )

    async def get_players(self, params: PlayerFilterParams) -> Tuple[List[PlayerListItemResponse], int]:
        players, total = await self.repo.get_players_filtered(params)
        items = [self._to_list_item(p) for p in players]
        return items, total

    async def get_player_profile(self, player_id: int) -> Optional[PlayerDetailResponse]:
        p = await self.repo.get_player_full_profile(player_id)
        if not p:
            return None

        base_item = self._to_list_item(p)
        active_injuries = [inj for inj in p.injuries if inj.active]
        active_suspensions = [susp for susp in p.suspensions if susp.active]

        # Compute or build rich metric response
        metric_resp = None
        if p.metric:
            # Reconstruct rich explainability
            metric_resp = AnalyticsEngine.compute_player_intelligence(
                player_id=p.id,
                recent_scores=[s.score for s in p.scores if s.score is not None],
                recent_minutes=[90 for _ in p.scores],
                recent_starts=len(p.scores),
                is_injured=len(active_injuries) > 0,
                injury_kind=active_injuries[0].kind if active_injuries else None,
                injury_status=active_injuries[0].status if active_injuries else None,
                is_suspended=len(active_suspensions) > 0,
                suspension_reason=active_suspensions[0].reason if active_suspensions else None,
                current_price=base_item.current_floor_price,
                avg_30d_price=(base_item.current_floor_price * 1.1) if base_item.current_floor_price else None,
            )

        recent_scores_resp = [
            PlayerGameScoreResponse.model_validate(s) for s in p.scores[:10]
        ]
        cards_resp = [CardResponse.model_validate(c) for c in p.cards]

        return PlayerDetailResponse(
            **base_item.model_dump(),
            metric=metric_resp,
            active_injuries=active_injuries,
            active_suspensions=active_suspensions,
            recent_scores=recent_scores_resp,
            cards=cards_resp,
        )

    async def get_player_scores(self, player_id: int, limit: int = 15) -> List[PlayerGameScoreResponse]:
        scores = await self.repo.get_player_scores(player_id, limit)
        return [PlayerGameScoreResponse.model_validate(s) for s in scores]

    async def get_player_fixtures(self, player_id: int, limit: int = 5) -> List[GameResponse]:
        games = await self.repo.get_player_fixtures(player_id, limit)
        return [GameResponse.model_validate(g) for g in games]

    async def get_player_news(self, player_id: int, limit: int = 10) -> List[NewsResponse]:
        news_items = await self.repo.get_player_news(player_id, limit)
        return [NewsResponse.model_validate(n) for n in news_items]
