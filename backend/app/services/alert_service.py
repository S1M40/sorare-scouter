from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertResponse, AlertMarkReadResponse


class AlertService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AlertRepository(session)

    async def get_user_alerts(self, user_id: int, unread_only: bool = False, limit: int = 50) -> List[AlertResponse]:
        alerts = await self.repo.get_user_alerts(user_id, unread_only, limit=limit)
        responses = []
        for a in alerts:
            responses.append(
                AlertResponse(
                    id=a.id,
                    user_id=a.user_id,
                    player_id=a.player_id,
                    type=a.type,
                    title=a.title,
                    message=a.message,
                    severity=a.severity,
                    source_type=a.source_type,
                    read=a.read,
                    created_at=a.created_at,
                    player_name=a.player.display_name if a.player else None,
                )
            )
        return responses

    async def mark_read(self, alert_id: int, user_id: int) -> AlertMarkReadResponse:
        success = await self.repo.mark_read(alert_id, user_id)
        return AlertMarkReadResponse(success=success, updated_count=1 if success else 0)

    async def mark_all_read(self, user_id: int) -> AlertMarkReadResponse:
        count = await self.repo.mark_all_read(user_id)
        return AlertMarkReadResponse(success=True, updated_count=count)
