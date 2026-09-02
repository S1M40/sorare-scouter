from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class Suspension(Base, TimestampMixin):
    __tablename__ = "suspensions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    sorare_id = Column(String(128), unique=True, index=True, nullable=True)
    active = Column(Boolean, default=True, nullable=False, index=True)
    competition = Column(String(128), nullable=True)
    kind = Column(String(128), nullable=False)
    reason = Column(String(512), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    matches = Column(Integer, nullable=True)

    # Relationships
    player = relationship("Player", back_populates="suspensions")

    __table_args__ = (
        Index("ix_suspensions_player_active", "player_id", "active"),
    )
