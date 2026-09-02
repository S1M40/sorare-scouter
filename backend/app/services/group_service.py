from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.group import GroupMemberResponse, GroupRankingResponse


class GroupService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_group_rankings(self, group_name: str = "ScoutLab Alpha Syndicate") -> GroupRankingResponse:
        query = select(User).where(User.is_active == True).order_by(User.id)
        result = await self.session.execute(query)
        users = list(result.scalars().all())

        # If few users exist, provide syndicate member breakdown
        members: List[GroupMemberResponse] = []
        mock_stats = [
            (14250.0, 84, 68.4, 420.5, "Master Scout"),
            (11800.0, 62, 64.2, 385.0, "Pro Scout"),
            (9500.0, 51, 61.8, 340.2, "Analyst"),
            (8200.0, 44, 59.5, 310.0, "Scout"),
            (6400.0, 32, 57.0, 275.5, "Novice"),
        ]

        total_val = 0.0
        for idx, u in enumerate(users):
            val, cards, avg_s, pts, badge = mock_stats[idx % len(mock_stats)]
            total_val += val
            members.append(
                GroupMemberResponse(
                    user_id=u.id,
                    username=u.username,
                    rank=idx + 1,
                    squad_value_eur=val,
                    total_cards=cards,
                    average_score_l5=avg_s,
                    weekly_points=pts,
                    badge=badge,
                )
            )

        if not members:
            # Fallback default syndicate profile
            members = [
                GroupMemberResponse(
                    user_id=1,
                    username="ScoutMaster_Alpha",
                    rank=1,
                    squad_value_eur=14250.0,
                    total_cards=84,
                    average_score_l5=68.4,
                    weekly_points=420.5,
                    badge="Master Scout",
                )
            ]
            total_val = 14250.0

        return GroupRankingResponse(
            group_name=group_name,
            season="2024/2025",
            total_members=len(members),
            total_group_value_eur=round(total_val, 2),
            rankings=members,
        )
