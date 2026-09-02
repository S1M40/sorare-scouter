from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Competition
from app.schemas.competition import CompetitionResponse
from app.schemas.common import ApiResponse, ApiMeta

router = APIRouter(prefix="/competitions", tags=["Competitions"])


@router.get("", response_model=ApiResponse[list[CompetitionResponse]])
async def list_competitions(db: AsyncSession = Depends(get_db)):
    """List all competitions."""
    result = await db.execute(select(Competition).order_by(Competition.name))
    comps = result.scalars().all()
    return ApiResponse(data=[CompetitionResponse.model_validate(c) for c in comps], meta=ApiMeta(source="scoutlab"))
