from typing import Optional
from pydantic import BaseModel, ConfigDict


class ClubBase(BaseModel):
    name: str
    short_name: Optional[str] = None
    slug: str
    logo_url: Optional[str] = None
    country: Optional[str] = None


class ClubResponse(ClubBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sorare_id: Optional[str] = None
