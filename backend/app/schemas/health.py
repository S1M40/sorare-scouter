from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str  # healthy, degraded, unhealthy
    version: str
    environment: str
    database: str  # connected, error
    redis: str  # connected, memory_fallback, error
    sorare_api: str  # connected, offline, demo_mode
    last_synchronization: Optional[datetime] = None
    data_freshness: str  # fresh, stale, demo
    sync_jobs: Dict[str, str] = {}
