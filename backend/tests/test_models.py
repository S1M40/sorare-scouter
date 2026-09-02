from datetime import datetime, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import (
    Club,
    Competition,
    Player,
    Game,
    PlayerGameScore,
    Injury,
    Suspension,
    Card,
    CardPrice,
    SO5Fixture,
    PlayerMetric,
    User,
    Watchlist,
    Alert,
)


@pytest.mark.asyncio
async def test_create_models_and_relationships(db_session: AsyncSession):
    now = datetime.now(timezone.utc)

    # 1. Competition & Club
    comp = Competition(slug="test-league", name="Test League", country="Europe")
    club = Club(slug="fc-test", name="FC Test", short_name="FCT", country="France")
    db_session.add_all([comp, club])
    await db_session.flush()

    assert comp.id is not None
    assert club.id is not None

    # 2. Player
    player = Player(
        slug="test-striker",
        display_name="Test Striker",
        age=24,
        position="Forward",
        active_club_id=club.id,
        nationality="France",
    )
    db_session.add(player)
    await db_session.flush()

    assert player.id is not None
    await db_session.refresh(player, ["club"])
    assert player.club.name == "FC Test"

    # 3. Card & CardPrice
    card = Card(
        player_id=player.id,
        season_year=2024,
        rarity="limited",
        position="Forward",
    )
    db_session.add(card)
    await db_session.flush()

    price = CardPrice(
        card_id=card.id,
        price=120.50,
        currency="EUR",
        source="secondary_market",
    )
    db_session.add(price)
    await db_session.flush()

    assert price.id is not None
    await db_session.refresh(card, ["prices"])
    assert card.prices[0].price == 120.50

    # 4. Injury & Suspension
    injury = Injury(
        player_id=player.id,
        active=True,
        kind="Ankle Sprain",
        status="DOUBTFUL",
    )
    suspension = Suspension(
        player_id=player.id,
        active=False,
        kind="Yellow Cards",
        matches=1,
    )
    db_session.add_all([injury, suspension])
    await db_session.flush()

    # 5. SO5 Fixture & Game
    gw = SO5Fixture(
        event_name="Gameweek 100",
        game_week=100,
        start_date=now,
        end_date=now,
        state="opened",
    )
    db_session.add(gw)
    await db_session.flush()

    game = Game(
        home_club_id=club.id,
        away_club_id=club.id,
        competition_id=comp.id,
        date=now,
        status="SCHEDULED",
    )
    db_session.add(game)
    await db_session.flush()

    # Score
    score = PlayerGameScore(
        player_id=player.id,
        game_id=game.id,
        score=72.4,
        score_status="FINAL",
    )
    db_session.add(score)
    await db_session.flush()

    # Metric
    metric = PlayerMetric(
        player_id=player.id,
        scout_score=82.0,
        form_score=78.0,
        recommendation="BUY",
        starting_probability=90.0,
    )
    db_session.add(metric)
    await db_session.flush()

    # 6. User, Watchlist & Alert
    user = User(
        username="tester1",
        email="tester1@test.com",
        password_hash="fakehash",
    )
    db_session.add(user)
    await db_session.flush()

    wl = Watchlist(user_id=user.id, player_id=player.id, target_price=100.0)
    alert = Alert(user_id=user.id, player_id=player.id, title="Test Alert", message="Price dropped")
    db_session.add_all([wl, alert])
    await db_session.commit()

    # Verify query
    q = select(Player).where(Player.id == player.id)
    res = await db_session.execute(q)
    fetched_player = res.scalars().first()
    assert fetched_player.display_name == "Test Striker"
    assert fetched_player.metric.scout_score == 82.0
