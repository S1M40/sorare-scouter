from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import utc_now


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="SET NULL"), nullable=True, index=True)
    type = Column(String(64), nullable=False, default="PRICE_DROP", index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(32), nullable=False, default="INFO")  # INFO, WARNING, CRITICAL, SUCCESS
    source_type = Column(String(32), nullable=False, default="FACT")  # FACT, REPORT, PREDICTION
    read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="alerts", lazy="selectin")
    player = relationship("Player", back_populates="alerts", lazy="selectin")

    __table_args__ = (
        Index("ix_alerts_user_read", "user_id", "read"),
    )
