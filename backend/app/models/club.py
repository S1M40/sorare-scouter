from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class Club(Base, TimestampMixin):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sorare_id = Column(String(128), unique=True, index=True, nullable=True)
    slug = Column(String(128), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    short_name = Column(String(64), nullable=True)
    logo_url = Column(String(512), nullable=True)
    country = Column(String(128), nullable=True)
    competition_id = Column(Integer, ForeignKey("competitions.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    competition = relationship("Competition")
    players = relationship("Player", back_populates="club")
    home_games = relationship("Game", foreign_keys="[Game.home_club_id]", back_populates="home_club")
    away_games = relationship("Game", foreign_keys="[Game.away_club_id]", back_populates="away_club")
