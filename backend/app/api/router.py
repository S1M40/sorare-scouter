from fastapi import APIRouter
from app.api.endpoints import (
    dashboard,
    players,
    cards,
    fixtures,
    market,
    watchlist,
    alerts,
    news,
    group,
    auth,
    clubs,
    competitions,
    portfolio,
)

api_router = APIRouter()

api_router.include_router(dashboard.router)
api_router.include_router(players.router)
api_router.include_router(cards.router)
api_router.include_router(fixtures.router)
api_router.include_router(market.router)
api_router.include_router(watchlist.router)
api_router.include_router(alerts.router)
api_router.include_router(news.router)
api_router.include_router(group.router)
api_router.include_router(auth.router)
api_router.include_router(clubs.router)
api_router.include_router(competitions.router)
api_router.include_router(portfolio.router)
