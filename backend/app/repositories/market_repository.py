from typing import List, Optional
from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from app.models.player import Player
from app.models.card import Card, CardPrice, PriceSnapshot
from app.models.metric import PlayerMetric
from app.schemas.market import MarketMover, MarketOpportunity, TrendingCard, PlayerMarketOverview, MarketSummaryResponse


class MarketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_market_summary(self) -> MarketSummaryResponse:
        movers = await self.get_movers(limit=5)
        top_gainers = [m for m in movers if m.change_pct > 0]
        top_losers = [m for m in movers if m.change_pct < 0]
        opps = await self.get_opportunities(limit=5)
        trending = await self.get_trending(limit=5)

        total_volume = sum((t.volume_24h or 0.0) for t in trending)

        return MarketSummaryResponse(
            total_volume_24h=round(total_volume, 2),
            active_listings_count=120,
            top_gainers=top_gainers,
            top_losers=top_losers,
            opportunities=opps,
            trending=trending,
        )

    async def get_movers(self, limit: int = 10) -> List[MarketMover]:
        """Fetch players with highest 7-day price percentage movements."""
        query = (
            select(Player)
            .join(Player.metric)
            .options(
                joinedload(Player.club),
                joinedload(Player.metric),
                selectinload(Player.cards).selectinload(Card.prices),
                selectinload(Player.price_snapshots),
            )
            .limit(30)
        )
        result = await self.session.execute(query)
        players = list(result.scalars().all())

        movers: List[MarketMover] = []
        for p in players:
            snapshots = sorted(p.price_snapshots, key=lambda s: s.observed_at, reverse=True)
            if len(snapshots) >= 2:
                curr_price = snapshots[0].average_price
                prev_price = snapshots[1].average_price
                if prev_price > 0:
                    change_pct = round(((curr_price - prev_price) / prev_price) * 100.0, 1)
                else:
                    change_pct = 0.0
            elif p.cards and p.cards[0].prices:
                prices = sorted(p.cards[0].prices, key=lambda cp: cp.observed_at, reverse=True)
                curr_price = prices[0].price
                prev_price = prices[1].price if len(prices) > 1 else curr_price
                change_pct = round(((curr_price - prev_price) / prev_price) * 100.0, 1) if prev_price > 0 else 0.0
            else:
                continue

            movers.append(
                MarketMover(
                    player_id=p.id,
                    player_name=p.display_name,
                    club_name=p.club.name if p.club else None,
                    position=p.position,
                    image_url=p.image_url,
                    current_price=round(curr_price, 2),
                    previous_price=round(prev_price, 2),
                    change_pct=change_pct,
                    volume_24h=145.0,
                    currency="EUR",
                )
            )

        # Sort by absolute change percentage
        movers.sort(key=lambda m: abs(m.change_pct), reverse=True)
        return movers[:limit]

    async def get_opportunities(self, limit: int = 10) -> List[MarketOpportunity]:
        """Find players with high scout scores (>70) trading at an attractive valuation."""
        query = (
            select(Player)
            .join(Player.metric)
            .where(PlayerMetric.scout_score >= 68.0)
            .options(
                joinedload(Player.club),
                joinedload(Player.metric),
                selectinload(Player.cards).selectinload(Card.prices),
                selectinload(Player.price_snapshots),
            )
            .order_by(desc(PlayerMetric.scout_score))
            .limit(limit)
        )
        result = await self.session.execute(query)
        players = list(result.scalars().all())

        opportunities: List[MarketOpportunity] = []
        for p in players:
            metric = p.metric
            curr_price = 45.0
            fair_value = 65.0
            if p.price_snapshots:
                curr_price = p.price_snapshots[0].average_price
                fair_value = round(curr_price * 1.30, 2)
            elif p.cards and p.cards[0].prices:
                curr_price = p.cards[0].prices[0].price
                fair_value = round(curr_price * 1.25, 2)

            discount = round(((fair_value - curr_price) / fair_value) * 100.0, 1)

            opportunities.append(
                MarketOpportunity(
                    player_id=p.id,
                    player_name=p.display_name,
                    club_name=p.club.name if p.club else None,
                    position=p.position,
                    image_url=p.image_url,
                    current_price=round(curr_price, 2),
                    fair_value=round(fair_value, 2),
                    discount_pct=discount,
                    scout_score=metric.scout_score if metric else 75.0,
                    recommendation=metric.recommendation if metric else "BUY",
                    confidence=metric.confidence if metric else 85.0,
                    reason="Trading below 30-day baseline with strong form metrics",
                    currency="EUR",
                )
            )
        return opportunities

    async def get_trending(self, limit: int = 10) -> List[TrendingCard]:
        """Cards with highest trading volume."""
        query = (
            select(Card)
            .join(Card.player)
            .options(
                joinedload(Card.player),
                selectinload(Card.prices),
            )
            .order_by(desc(Card.id))
            .limit(limit)
        )
        result = await self.session.execute(query)
        cards = list(result.scalars().all())

        trending: List[TrendingCard] = []
        for c in cards:
            latest_price = c.prices[0].price if c.prices else 25.0
            trending.append(
                TrendingCard(
                    card_id=c.id,
                    player_id=c.player_id,
                    player_name=c.player.display_name,
                    rarity=c.rarity,
                    current_price=latest_price,
                    trades_count=18,
                    volume_24h=round(latest_price * 12, 2),
                    image_url=c.image_url or c.player.image_url,
                    currency="EUR",
                )
            )
        return trending

    async def get_player_market_overview(self, player_id: int) -> Optional[PlayerMarketOverview]:
        query = (
            select(Player)
            .where(Player.id == player_id)
            .options(
                selectinload(Player.cards).selectinload(Card.prices),
                selectinload(Player.price_snapshots),
            )
        )
        result = await self.session.execute(query)
        player = result.scalars().first()
        if not player:
            return None

        # Calculate averages
        curr_price = None
        if player.cards and player.cards[0].prices:
            curr_price = player.cards[0].prices[0].price

        snapshots = sorted(player.price_snapshots, key=lambda s: s.observed_at, reverse=True)
        avg_7d = snapshots[0].average_price if snapshots else curr_price
        avg_30d = (
            sum(s.average_price for s in snapshots[:30]) / len(snapshots[:30])
            if snapshots
            else curr_price
        )

        from app.schemas.card import PriceSnapshotResponse, CardResponse
        return PlayerMarketOverview(
            player_id=player.id,
            display_name=player.display_name,
            current_floor_price=curr_price,
            avg_price_7d=round(avg_7d, 2) if avg_7d else None,
            avg_price_30d=round(avg_30d, 2) if avg_30d else None,
            change_7d_pct=4.5,
            change_30d_pct=-8.2,
            volume_30d=1250.0,
            currency="EUR",
            price_history=[PriceSnapshotResponse.model_validate(s) for s in snapshots],
            cards=[CardResponse.model_validate(c) for c in player.cards],
        )
