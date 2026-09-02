from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class Injury(Base, TimestampMixin):
    __tablename__ = "injuries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    sorare_id = Column(String(128), unique=True, index=True, nullable=True)
    active = Column(Boolean, default=True, nullable=False, index=True)
    kind = Column(String(128), nullable=False)
    details = Column(String(512), nullable=True)
    status = Column(String(64), nullable=False, default="OUT")
    start_date = Column(DateTime(timezone=True), nullable=True)
    expected_end_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    player = relationship("Player", back_populates="injuries")

    __table_args__ = (
        Index("ix_injuries_player_active", "player_id", "active"),
    )
