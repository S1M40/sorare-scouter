from sqlalchemy import Column, Integer, String, DateTime, Index
from app.database import Base
from app.models.base import TimestampMixin


class SO5Fixture(Base, TimestampMixin):
    __tablename__ = "so5_fixtures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sorare_id = Column(String(128), unique=True, index=True, nullable=True)
    event = Column(String(64), nullable=True, default="football")
    event_name = Column(String(128), nullable=False)
    event_type = Column(String(64), nullable=True)
    game_week = Column(Integer, nullable=False, index=True)
    start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    end_date = Column(DateTime(timezone=True), nullable=False)
    cutoff_date = Column(DateTime(timezone=True), nullable=True)
    state = Column(String(32), nullable=False, default="upcoming", index=True)  # upcoming, opened, live, closed

    __table_args__ = (
        Index("ix_so5_fixtures_gw_state", "game_week", "state"),
    )
