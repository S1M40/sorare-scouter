from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import utc_now


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    url = Column(String(512), nullable=True)
    source = Column(String(128), nullable=False)
    published_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    category = Column(String(64), nullable=False, default="general", index=True)
    summary = Column(Text, nullable=True)
    source_type = Column(String(32), nullable=False, default="REPORT")  # FACT, REPORT, PREDICTION
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    player_links = relationship("NewsPlayerLink", back_populates="news", cascade="all, delete-orphan")


class NewsPlayerLink(Base):
    __tablename__ = "news_player_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    news = relationship("News", back_populates="player_links")
    player = relationship("Player", back_populates="news_links")

    __table_args__ = (
        Index("ix_news_player", "news_id", "player_id", unique=True),
    )
