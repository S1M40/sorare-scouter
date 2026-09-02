from math import ceil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse, ApiListResponse, ApiPaginationMeta, ApiMeta
from app.schemas.news import NewsResponse
from app.services.news_service import NewsService

router = APIRouter(prefix="/news", tags=["News"])


@router.get("", response_model=ApiListResponse[NewsResponse])
async def list_news(
    category: Optional[str] = Query(None, description="injury, transfer, tactical, general"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = NewsService(db)
    items, total = await service.get_news(category=category, page=page, page_size=page_size)
    total_pages = ceil(total / page_size) if total > 0 else 1
    meta = ApiPaginationMeta(
        page=page, page_size=page_size, total=total, total_pages=total_pages, source="scoutlab"
    )
    return ApiListResponse(data=items, meta=meta)


@router.get("/{news_id}", response_model=ApiResponse[NewsResponse])
async def get_news_item(news_id: int, db: AsyncSession = Depends(get_db)):
    service = NewsService(db)
    news = await service.get_news_by_id(news_id)
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News item not found")
    return ApiResponse(data=news, meta=ApiMeta(source="scoutlab"))
