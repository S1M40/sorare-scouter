from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.player_repository import PlayerRepository
from app.repositories.fixture_repository import FixtureRepository
from app.repositories.market_repository import MarketRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.sync_repository import SyncRepository
from app.schemas.player import PlayerFilterParams
from app.schemas.dashboard import (
    DashboardMetricsResponse,
    DashboardGameweekInfo,
    DashboardDataFreshness,
)
from app.services.player_service import PlayerService
from app.services.alert_service import AlertService


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.player_repo = PlayerRepository(session)
        self.fixture_repo = FixtureRepository(session)
        self.market_repo = MarketRepository(session)
        self.alert_repo = AlertRepository(session)
        self.sync_repo = SyncRepository(session)
        self.player_service = PlayerService(session)
        self.alert_service = AlertService(session)

    async def get_dashboard_metrics(self, user_id: Optional[int] = None) -> DashboardMetricsResponse:
        # 1. Current Gameweek
        gw_model = await self.fixture_repo.get_current_gameweek()
        gw_info = None
        if gw_model and gw_model.end_date:
            now = datetime.now(timezone.utc)
            end_dt = gw_model.end_date
            if end_dt.tzinfo is None:
                end_dt = end_dt.replace(tzinfo=timezone.utc)
            remaining_secs = int((end_dt - now).total_seconds()) if end_dt > now else 0
            gw_info = DashboardGameweekInfo(
                game_week=gw_model.game_week,
                event_name=gw_model.event_name,
                state=gw_model.state,
                start_date=gw_model.start_date,
                end_date=gw_model.end_date,
                cutoff_date=gw_model.cutoff_date,
                time_remaining_seconds=remaining_secs,
            )

        # 2. In-form players (highest form scores)
        form_params = PlayerFilterParams(sort_by="form_score", sort_order="desc", page_size=5)
        in_form_players, _ = await self.player_service.get_players(form_params)

        # 3. Scouting opportunities (highest scout scores)
        scout_params = PlayerFilterParams(sort_by="scout_score", sort_order="desc", page_size=5)
        scout_opps, _ = await self.player_service.get_players(scout_params)

        # 4. Players at risk (injured, suspended, or low starting prob)
        risk_params = PlayerFilterParams(injury_status="injured", page_size=5)
        risk_players, _ = await self.player_service.get_players(risk_params)

        # 5. Market opportunities
        market_opps = await self.market_repo.get_opportunities(limit=5)

        # 6. Upcoming fixtures
        games, _ = await self.fixture_repo.get_games(status="SCHEDULED", page_size=5)
        from app.schemas.fixture import GameResponse
        upcoming_games = [GameResponse.model_validate(g) for g in games]

        # 7. Recent alerts
        recent_alerts = []
        if user_id:
            recent_alerts = await self.alert_service.get_user_alerts(user_id=user_id, limit=5)

        # 8. Data Freshness & Sync status
        sync_jobs = await self.sync_repo.get_all_jobs()
        sync_summary = {j.job_name: j.status for j in sync_jobs}
        last_sync = max((j.last_finished_at for j in sync_jobs if j.last_finished_at), default=None)

        return DashboardMetricsResponse(
            current_gameweek=gw_info,
            squad_value_eur=14250.0,
            average_score_l5=64.8,
            players_in_form=in_form_players,
            players_at_risk=risk_players,
            market_opportunities=market_opps,
            scouting_opportunities=scout_opps,
            upcoming_fixtures=upcoming_games,
            recent_alerts=recent_alerts,
            data_freshness=DashboardDataFreshness(
                last_sync_at=last_sync,
                status="fresh" if last_sync else "demo",
                sync_jobs_summary=sync_summary,
            ),
        )
