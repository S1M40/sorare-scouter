from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.common import SourceTypeEnum


class NewsPlayerItem(BaseModel):
    id: int
    display_name: str
    slug: str
    image_url: Optional[str] = None


class NewsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    url: Optional[str] = None
    source: str
    published_at: datetime
    category: str
    summary: Optional[str] = None
    source_type: SourceTypeEnum
    created_at: datetime
    players: List[NewsPlayerItem] = []
