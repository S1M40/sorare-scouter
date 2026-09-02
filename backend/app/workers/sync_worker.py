import asyncio
import logging
from app.config import settings
from app.database import AsyncSessionLocal
from app.services.sync_service import SyncService

logger = logging.getLogger(__name__)


class SyncWorker:
    """Background synchronization worker executing periodic reconciliations."""

    def __init__(self, interval_minutes: int = 30):
        self.interval_seconds = interval_minutes * 60
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"SyncWorker started with {self.interval_seconds}s interval.")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("SyncWorker stopped.")

    async def _run_loop(self) -> None:
        # Initial run shortly after startup
        await asyncio.sleep(5)
        while self._running:
            try:
                logger.info("Starting background synchronization cycle...")
                async with AsyncSessionLocal() as session:
                    service = SyncService(session)
                    results = await service.run_all_jobs()
                    await session.commit()
                logger.info(f"Background synchronization cycle finished: {results}")
            except Exception as e:
                logger.error(f"Error during background sync cycle: {e}", exc_info=True)

            # Wait for next interval
            try:
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                break


sync_worker = SyncWorker(interval_minutes=settings.SYNC_INTERVAL_MINUTES)
