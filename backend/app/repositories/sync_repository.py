from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sync_status import SyncStatus
from app.repositories.base import BaseRepository


class SyncRepository(BaseRepository[SyncStatus]):
    def __init__(self, session: AsyncSession):
        super().__init__(SyncStatus, session)

    async def get_all_jobs(self) -> List[SyncStatus]:
        query = select(SyncStatus).order_by(SyncStatus.job_name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_job_name(self, job_name: str) -> Optional[SyncStatus]:
        query = select(SyncStatus).where(SyncStatus.job_name == job_name)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def record_start(self, job_name: str) -> SyncStatus:
        status = await self.get_by_job_name(job_name)
        now = datetime.now(timezone.utc)
        if not status:
            status = SyncStatus(
                job_name=job_name,
                status="RUNNING",
                last_started_at=now,
                records_processed=0,
            )
            self.session.add(status)
        else:
            status.status = "RUNNING"
            status.last_started_at = now
            status.error_message = None
        await self.session.flush()
        return status

    async def record_success(self, job_name: str, records_processed: int) -> SyncStatus:
        status = await self.get_by_job_name(job_name)
        now = datetime.now(timezone.utc)
        if not status:
            status = SyncStatus(
                job_name=job_name,
                status="SUCCESS",
                last_finished_at=now,
                records_processed=records_processed,
            )
            self.session.add(status)
        else:
            status.status = "SUCCESS"
            status.last_finished_at = now
            status.records_processed = records_processed
            status.error_message = None
        await self.session.flush()
        return status

    async def record_failure(self, job_name: str, error_message: str) -> SyncStatus:
        status = await self.get_by_job_name(job_name)
        now = datetime.now(timezone.utc)
        if not status:
            status = SyncStatus(
                job_name=job_name,
                status="FAILED",
                last_finished_at=now,
                error_message=error_message,
            )
            self.session.add(status)
        else:
            status.status = "FAILED"
            status.last_finished_at = now
            status.error_message = error_message
        await self.session.flush()
        return status
