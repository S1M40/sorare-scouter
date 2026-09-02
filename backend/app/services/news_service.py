from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.news_repository import NewsRepository
from app.schemas.news import NewsResponse, NewsPlayerItem


class NewsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = NewsRepository(session)

    async def get_news(
        self, category: Optional[str] = None, page: int = 1, page_size: int = 25
    ) -> Tuple[List[NewsResponse], int]:
        news_list, total = await self.repo.get_news_list(category, page, page_size)
        results = []
        for n in news_list:
            players = [
                NewsPlayerItem(
                    id=l.player.id,
                    display_name=l.player.display_name,
                    slug=l.player.slug,
                    image_url=l.player.image_url,
                )
                for l in n.player_links
                if l.player
            ]
            results.append(
                NewsResponse(
                    id=n.id,
                    title=n.title,
                    url=n.url,
                    source=n.source,
                    published_at=n.published_at,
                    category=n.category,
                    summary=n.summary,
                    source_type=n.source_type,
                    created_at=n.created_at,
                    players=players,
                )
            )
        return results, total

    async def get_news_by_id(self, news_id: int) -> Optional[NewsResponse]:
        n = await self.repo.get_news_detail(news_id)
        if not n:
            return None
        players = [
            NewsPlayerItem(
                id=l.player.id,
                display_name=l.player.display_name,
                slug=l.player.slug,
                image_url=l.player.image_url,
            )
            for l in n.player_links
            if l.player
        ]
        return NewsResponse(
            id=n.id,
            title=n.title,
            url=n.url,
            source=n.source,
            published_at=n.published_at,
            category=n.category,
            summary=n.summary,
            source_type=n.source_type,
            created_at=n.created_at,
            players=players,
        )
