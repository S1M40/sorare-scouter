from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class Player(Base, TimestampMixin):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sorare_id = Column(String(128), unique=True, index=True, nullable=True)
    slug = Column(String(128), index=True, nullable=False)
    display_name = Column(String(255), nullable=False, index=True)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    age = Column(Integer, nullable=True, index=True)
    position = Column(String(64), nullable=False, index=True)
    active_club_id = Column(Integer, ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True, index=True)
    nationality = Column(String(128), nullable=True)
    image_url = Column(String(512), nullable=True)

    # Relationships
    club = relationship("Club", back_populates="players", lazy="selectin")
    scores = relationship("PlayerGameScore", back_populates="player", cascade="all, delete-orphan", lazy="selectin")
    injuries = relationship("Injury", back_populates="player", cascade="all, delete-orphan", lazy="selectin")
    suspensions = relationship("Suspension", back_populates="player", cascade="all, delete-orphan", lazy="selectin")
    cards = relationship("Card", back_populates="player", cascade="all, delete-orphan", lazy="selectin")
    metric = relationship("PlayerMetric", back_populates="player", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    price_snapshots = relationship("PriceSnapshot", back_populates="player", cascade="all, delete-orphan", lazy="selectin")
    score_snapshots = relationship("ScoreSnapshot", back_populates="player", cascade="all, delete-orphan", lazy="selectin")
    news_links = relationship("NewsPlayerLink", back_populates="player", cascade="all, delete-orphan", lazy="selectin")
    watchlists = relationship("Watchlist", back_populates="player", cascade="all, delete-orphan", lazy="selectin")
    alerts = relationship("Alert", back_populates="player", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("ix_players_pos_club", "position", "active_club_id"),
    )
