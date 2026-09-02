from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base
from app.models.base import utc_now


class SyncStatus(Base):
    __tablename__ = "sync_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(128), unique=True, index=True, nullable=False)
    status = Column(String(32), default="IDLE", nullable=False)  # IDLE, RUNNING, SUCCESS, FAILED
    last_started_at = Column(DateTime(timezone=True), nullable=True)
    last_finished_at = Column(DateTime(timezone=True), nullable=True)
    records_processed = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
