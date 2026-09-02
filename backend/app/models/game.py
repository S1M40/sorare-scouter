from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class Game(Base, TimestampMixin):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sorare_id = Column(String(128), unique=True, index=True, nullable=True)
    home_club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True)
    away_club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True)
    competition_id = Column(Integer, ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String(64), nullable=False, default="SCHEDULED", index=True)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    minute = Column(Integer, nullable=True)
    coverage_status = Column(String(64), nullable=True)

    # Relationships
    home_club = relationship("Club", foreign_keys=[home_club_id], back_populates="home_games")
    away_club = relationship("Club", foreign_keys=[away_club_id], back_populates="away_games")
    competition = relationship("Competition", back_populates="games")
    scores = relationship("PlayerGameScore", back_populates="game", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_games_date_status", "date", "status"),
    )
