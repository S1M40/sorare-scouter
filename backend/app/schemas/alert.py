from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.common import SeverityEnum, SourceTypeEnum


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    player_id: Optional[int] = None
    type: str
    title: str
    message: str
    severity: SeverityEnum
    source_type: SourceTypeEnum
    read: bool
    created_at: datetime
    player_name: Optional[str] = None


class AlertMarkReadResponse(BaseModel):
    success: bool
    updated_count: int
