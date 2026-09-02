from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Club
from app.schemas.club import ClubResponse
from app.schemas.common import ApiResponse, ApiMeta

router = APIRouter(prefix="/clubs", tags=["Clubs"])


@router.get("", response_model=ApiResponse[list[ClubResponse]])
async def list_clubs(db: AsyncSession = Depends(get_db)):
    """List all clubs in the database."""
    result = await db.execute(select(Club).order_by(Club.name))
    clubs = result.scalars().all()
    return ApiResponse(data=[ClubResponse.model_validate(c) for c in clubs], meta=ApiMeta(source="scoutlab"))
