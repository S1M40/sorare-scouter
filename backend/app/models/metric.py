from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import utc_now


class PlayerMetric(Base):
    __tablename__ = "player_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    form_score = Column(Float, nullable=False, default=0.0)
    consistency_score = Column(Float, nullable=False, default=0.0)
    minutes_score = Column(Float, nullable=False, default=0.0)
    fixture_score = Column(Float, nullable=False, default=0.0)
    market_score = Column(Float, nullable=False, default=0.0)
    availability_score = Column(Float, nullable=False, default=100.0)
    scout_score = Column(Float, nullable=False, default=0.0, index=True)
    risk_score = Column(Float, nullable=False, default=0.0)
    risk_level = Column(String(32), nullable=False, default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    starting_probability = Column(Float, nullable=False, default=50.0, index=True)
    recommendation = Column(String(32), nullable=False, default="HOLD", index=True)  # BUY, WATCH, HOLD, SELL, AVOID
    confidence = Column(Float, nullable=False, default=70.0)
    calculated_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationships
    player = relationship("Player", back_populates="metric")

    __table_args__ = (
        Index("ix_metrics_scout_rec", "scout_score", "recommendation"),
    )
