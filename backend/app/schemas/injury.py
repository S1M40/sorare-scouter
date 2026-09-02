from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.common import SourceTypeEnum


class InjuryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    player_id: int
    sorare_id: Optional[str] = None
    active: bool
    kind: str
    details: Optional[str] = None
    status: str
    start_date: Optional[datetime] = None
    expected_end_date: Optional[datetime] = None
    source_type: SourceTypeEnum = SourceTypeEnum.FACT


class SuspensionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    player_id: int
    sorare_id: Optional[str] = None
    active: bool
    competition: Optional[str] = None
    kind: str
    reason: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    matches: Optional[int] = None
    source_type: SourceTypeEnum = SourceTypeEnum.FACT
