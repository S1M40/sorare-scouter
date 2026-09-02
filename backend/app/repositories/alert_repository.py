from typing import List, Optional
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models.alert import Alert
from app.models.player import Player
from app.repositories.base import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    def __init__(self, session: AsyncSession):
        super().__init__(Alert, session)

    async def get_user_alerts(
        self, user_id: int, unread_only: bool = False, limit: int = 50
    ) -> List[Alert]:
        query = (
            select(Alert)
            .where(Alert.user_id == user_id)
            .options(joinedload(Alert.player))
        )
        if unread_only:
            query = query.where(Alert.read == False)
        query = query.order_by(desc(Alert.created_at)).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def mark_read(self, alert_id: int, user_id: int) -> bool:
        stmt = (
            update(Alert)
            .where(Alert.id == alert_id, Alert.user_id == user_id)
            .values(read=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def mark_all_read(self, user_id: int) -> int:
        stmt = (
            update(Alert)
            .where(Alert.user_id == user_id, Alert.read == False)
            .values(read=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount
