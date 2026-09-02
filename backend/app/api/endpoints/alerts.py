from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse, ApiMeta
from app.schemas.alert import AlertResponse, AlertMarkReadResponse
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=ApiResponse[List[AlertResponse]])
async def get_alerts(
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AlertService(db)
    alerts = await service.get_user_alerts(user_id=current_user.id, unread_only=unread_only)
    return ApiResponse(data=alerts, meta=ApiMeta(source="scoutlab"))


@router.post("/{alert_id}/read", response_model=ApiResponse[AlertMarkReadResponse])
async def mark_alert_as_read(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AlertService(db)
    resp = await service.mark_read(alert_id=alert_id, user_id=current_user.id)
    return ApiResponse(data=resp, meta=ApiMeta(source="scoutlab"))


@router.post("/read-all", response_model=ApiResponse[AlertMarkReadResponse])
async def mark_all_alerts_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AlertService(db)
    resp = await service.mark_all_read(user_id=current_user.id)
    return ApiResponse(data=resp, meta=ApiMeta(source="scoutlab"))
