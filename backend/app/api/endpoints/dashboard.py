from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_optional_current_user
from app.models.user import User
from app.schemas.common import ApiResponse, ApiMeta
from app.schemas.dashboard import DashboardMetricsResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=ApiResponse[DashboardMetricsResponse])
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Retrieve full dashboard overview including gameweek, squad valuation, form, risks, and market highlights."""
    service = DashboardService(db)
    user_id = current_user.id if current_user else None
    data = await service.get_dashboard_metrics(user_id=user_id)
    return ApiResponse(data=data, meta=ApiMeta(source="scoutlab"))
