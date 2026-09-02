from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin, utc_now


class Card(Base, TimestampMixin):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sorare_id = Column(String(128), unique=True, index=True, nullable=True)
    asset_id = Column(String(128), index=True, nullable=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    season_year = Column(Integer, nullable=False, index=True)
    rarity = Column(String(64), nullable=False, index=True)  # limited, rare, super_rare, unique
    position = Column(String(64), nullable=True)
    power = Column(Float, default=0.0)
    grade = Column(String(32), nullable=True)
    image_url = Column(String(512), nullable=True)

    # Relationships
    player = relationship("Player", back_populates="cards", lazy="selectin")
    prices = relationship("CardPrice", back_populates="card", cascade="all, delete-orphan", lazy="selectin")
    price_snapshots = relationship("PriceSnapshot", back_populates="card", cascade="all, delete-orphan", lazy="selectin")


class CardPrice(Base):
    __tablename__ = "card_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(16), nullable=False, default="EUR")
    source = Column(String(64), nullable=False, default="secondary_market")  # auction, secondary_market, direct_offer
    observed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationships
    card = relationship("Card", back_populates="prices")

    __table_args__ = (
        Index("ix_card_prices_card_observed", "card_id", "observed_at"),
    )


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("cards.id", ondelete="SET NULL"), nullable=True, index=True)
    average_price = Column(Float, nullable=False)
    lowest_ask = Column(Float, nullable=True)
    highest_bid = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    currency = Column(String(16), nullable=False, default="EUR")
    observed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationships
    player = relationship("Player", back_populates="price_snapshots")
    card = relationship("Card", back_populates="price_snapshots")

    __table_args__ = (
        Index("ix_price_snapshots_player_observed", "player_id", "observed_at"),
    )
