from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse, ApiMeta
from app.schemas.group import GroupRankingResponse
from app.services.group_service import GroupService

router = APIRouter(prefix="/group", tags=["Group"])


@router.get("", response_model=ApiResponse[GroupRankingResponse])
async def get_group_overview(db: AsyncSession = Depends(get_db)):
    """Retrieve private syndicate group overview and leaderboard."""
    service = GroupService(db)
    rankings = await service.get_group_rankings()
    return ApiResponse(data=rankings, meta=ApiMeta(source="scoutlab"))


@router.get("/ranking", response_model=ApiResponse[GroupRankingResponse])
async def get_group_ranking(db: AsyncSession = Depends(get_db)):
    """Retrieve leaderboard ranking among syndicate members."""
    service = GroupService(db)
    rankings = await service.get_group_rankings()
    return ApiResponse(data=rankings, meta=ApiMeta(source="scoutlab"))
