from typing import Optional
from pydantic import BaseModel, ConfigDict


class CompetitionBase(BaseModel):
    name: str
    slug: str
    country: Optional[str] = None


class CompetitionResponse(CompetitionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sorare_id: Optional[str] = None
