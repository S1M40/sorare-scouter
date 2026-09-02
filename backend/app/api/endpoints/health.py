from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.config import settings
from app.utils.redis_client import cache
from app.repositories.sync_repository import SyncRepository
from app.schemas.health import HealthCheckResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive system health check: DB, Redis, Sorare, and sync freshness."""
    # 1. Database check
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    # 2. Redis check
    redis_status = "connected" if cache.is_connected else "memory_fallback"

    # 3. Sorare API check
    if settings.DEMO_MODE:
        sorare_status = "demo_mode"
    elif settings.SORARE_API_KEY:
        sorare_status = "connected"
    else:
        sorare_status = "not_configured"

    # 4. Synchronization status
    sync_repo = SyncRepository(db)
    sync_jobs = await sync_repo.get_all_jobs()
    job_summary = {j.job_name: j.status for j in sync_jobs}
    last_sync = max((j.last_finished_at for j in sync_jobs if j.last_finished_at), default=None)

    freshness = "demo"
    if last_sync:
        if last_sync.tzinfo is None:
            last_sync = last_sync.replace(tzinfo=timezone.utc)
        age_seconds = (datetime.now(timezone.utc) - last_sync).total_seconds()
        freshness = "fresh" if age_seconds < 3600 else "stale"

    overall = "healthy" if db_status == "connected" else "degraded"

    return HealthCheckResponse(
        status=overall,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
        redis=redis_status,
        sorare_api=sorare_status,
        last_synchronization=last_sync,
        data_freshness=freshness,
        sync_jobs=job_summary,
    )
