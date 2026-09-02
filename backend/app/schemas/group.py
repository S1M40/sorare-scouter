from typing import List, Optional
from pydantic import BaseModel


class GroupMemberResponse(BaseModel):
    user_id: int
    username: str
    rank: int
    squad_value_eur: float
    total_cards: int
    average_score_l5: float
    weekly_points: float
    badge: Optional[str] = "Scout"


class GroupRankingResponse(BaseModel):
    group_name: str
    season: str
    total_members: int
    total_group_value_eur: float
    rankings: List[GroupMemberResponse] = []
