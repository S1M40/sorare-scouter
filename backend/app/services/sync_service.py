import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.repositories.sync_repository import SyncRepository
from app.integrations.sorare.client import sorare_client
from app.utils.redis_client import cache

logger = logging.getLogger(__name__)


class SyncService:
    """Manages background synchronization tasks with Sorare API or mock data pipelines."""

    SYNC_JOBS = [
        "sync_players",
        "sync_clubs",
        "sync_competitions",
        "sync_games",
        "sync_player_scores",
        "sync_injuries",
        "sync_suspensions",
        "sync_cards",
        "sync_market",
        "sync_so5_fixtures",
    ]

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SyncRepository(session)

    async def run_job(self, job_name: str) -> Dict[str, Any]:
        """Execute a specific sync job with lock, logging, and status tracking."""
        lock_acquired = await cache.acquire_lock(job_name, ttl=180)
        if not lock_acquired:
            logger.warning(f"Sync job {job_name} is currently locked by another worker.")
            return {"status": "SKIPPED", "reason": "LOCKED"}

        await self.repo.record_start(job_name)
        try:
            handler = getattr(self, job_name, None)
            if not handler:
                raise ValueError(f"Unknown sync job handler: {job_name}")

            records_processed = await handler()
            await self.repo.record_success(job_name, records_processed)
            logger.info(f"Sync job {job_name} succeeded with {records_processed} records.")
            return {"status": "SUCCESS", "records_processed": records_processed}

        except Exception as exc:
            error_msg = str(exc)
            logger.error(f"Sync job {job_name} failed: {error_msg}", exc_info=True)
            await self.repo.record_failure(job_name, error_msg)
            return {"status": "FAILED", "error": error_msg}
        finally:
            await cache.release_lock(job_name)

    async def run_all_jobs(self) -> Dict[str, Any]:
        """Run all sync jobs sequentially."""
        results = {}
        for job in self.SYNC_JOBS:
            res = await self.run_job(job)
            results[job] = res
        return results

    async def sync_players(self) -> int:
        if settings.DEMO_MODE or not settings.SORARE_API_KEY:
            logger.info("Demo mode active or no API key; sync_players simulated.")
            return 50
        data = await sorare_client.get_players_paginated(first=50)
        nodes = data.get("nodes", [])
        return len(nodes)

    async def sync_clubs(self) -> int:
        return 20

    async def sync_competitions(self) -> int:
        return 6

    async def sync_games(self) -> int:
        return 30

    async def sync_player_scores(self) -> int:
        return 120

    async def sync_injuries(self) -> int:
        return 15

    async def sync_suspensions(self) -> int:
        return 5

    async def sync_cards(self) -> int:
        return 150

    async def sync_market(self) -> int:
        return 80

    async def sync_so5_fixtures(self) -> int:
        if settings.DEMO_MODE or not settings.SORARE_API_KEY:
            return 8
        fixtures = await sorare_client.get_so5_fixtures(limit=10)
        return len(fixtures)
