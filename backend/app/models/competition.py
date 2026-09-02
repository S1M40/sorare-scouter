from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class Competition(Base, TimestampMixin):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sorare_id = Column(String(128), unique=True, index=True, nullable=True)
    slug = Column(String(128), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    country = Column(String(128), nullable=True)

    # Relationships
    games = relationship("Game", back_populates="competition")
