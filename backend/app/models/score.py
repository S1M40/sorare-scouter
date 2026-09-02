from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin, utc_now


class PlayerGameScore(Base, TimestampMixin):
    __tablename__ = "player_game_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=True, index=True)
    average_score = Column(Float, nullable=True)
    projected_score = Column(Float, nullable=True)
    projection_grade = Column(String(32), nullable=True)
    projection_reliability = Column(Float, nullable=True)
    decisive_score = Column(Float, nullable=True)
    all_around_score = Column(Float, nullable=True)
    score_status = Column(String(64), nullable=True)
    scoring_version = Column(String(32), nullable=True)

    # Relationships
    player = relationship("Player", back_populates="scores")
    game = relationship("Game", back_populates="scores")

    __table_args__ = (
        Index("ix_scores_player_game", "player_id", "game_id"),
    )


class ScoreSnapshot(Base):
    __tablename__ = "score_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    l5_average = Column(Float, nullable=True)
    l15_average = Column(Float, nullable=True)
    l40_average = Column(Float, nullable=True)
    clean_sheet_rate = Column(Float, nullable=True)
    goal_rate = Column(Float, nullable=True)
    assist_rate = Column(Float, nullable=True)
    observed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationships
    player = relationship("Player", back_populates="score_snapshots")
