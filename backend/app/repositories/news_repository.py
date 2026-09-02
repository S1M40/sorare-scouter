from typing import List, Optional, Tuple
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.news import News, NewsPlayerLink
from app.repositories.base import BaseRepository


class NewsRepository(BaseRepository[News]):
    def __init__(self, session: AsyncSession):
        super().__init__(News, session)

    async def get_news_list(
        self, category: Optional[str] = None, page: int = 1, page_size: int = 25
    ) -> Tuple[List[News], int]:
        query = select(News).options(
            selectinload(News.player_links).joinedload(NewsPlayerLink.player)
        )
        if category:
            query = query.where(News.category.ilike(category))

        count_subquery = query.with_only_columns(func.count(News.id)).order_by(None)
        total_res = await self.session.execute(count_subquery)
        total = total_res.scalar() or 0

        query = query.order_by(desc(News.published_at)).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_news_detail(self, news_id: int) -> Optional[News]:
        query = (
            select(News)
            .where(News.id == news_id)
            .options(selectinload(News.player_links).joinedload(NewsPlayerLink.player))
        )
        result = await self.session.execute(query)
        return result.scalars().first()
