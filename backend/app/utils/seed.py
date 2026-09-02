import asyncio
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, AsyncSessionLocal, init_db
from app.models import (
    Club,
    Competition,
    Player,
    Game,
    PlayerGameScore,
    ScoreSnapshot,
    Injury,
    Suspension,
    Card,
    CardPrice,
    PriceSnapshot,
    SO5Fixture,
    PlayerMetric,
    News,
    NewsPlayerLink,
    Watchlist,
    Alert,
    User,
    SyncStatus,
)
from app.utils.security import hash_password
from app.analytics.engine import AnalyticsEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_database(session: AsyncSession | None = None) -> None:
    if session is not None:
        await _seed_with_session(session)
    else:
        logger.info("Initializing tables before seeding...")
        await init_db()
        async with AsyncSessionLocal() as sess:
            await _seed_with_session(sess)


async def _seed_with_session(session: AsyncSession) -> None:
    # Check if database already has players
    from sqlalchemy import select, func
    existing_count = await session.scalar(select(func.count(Player.id)))
    if existing_count and existing_count >= 50:
        logger.info(f"Database already seeded with {existing_count} players. Skipping.")
        return

    logger.info("Populating realistic ScoutLab football intelligence data...")
    now = datetime.now(timezone.utc)

    # 1. Users
    pwd_hash = hash_password("password123")
    user1 = User(
        id=1,
        username="ScoutMaster_Alpha",
        email="admin@scoutlab.io",
        password_hash=pwd_hash,
        is_active=True,
        is_admin=True,
        group_name="ScoutLab Alpha Syndicate",
    )
    user2 = User(
        id=2,
        username="ProScout_Tactics",
        email="scout@scoutlab.io",
        password_hash=pwd_hash,
        is_active=True,
        is_admin=False,
        group_name="ScoutLab Alpha Syndicate",
    )
    user3 = User(
        id=3,
        username="SorareWhale_99",
        email="analyst@scoutlab.io",
        password_hash=pwd_hash,
        is_active=True,
        is_admin=False,
        group_name="ScoutLab Alpha Syndicate",
    )
    session.add_all([user1, user2, user3])
    await session.flush()

    # 2. Competitions
    comps = [
        Competition(id=1, sorare_id="comp_pl", slug="premier-league", name="Premier League", country="England"),
        Competition(id=2, sorare_id="comp_ll", slug="la-liga", name="La Liga", country="Spain"),
        Competition(id=3, sorare_id="comp_ucl", slug="champions-league", name="UEFA Champions League", country="Europe"),
        Competition(id=4, sorare_id="comp_bl", slug="bundesliga", name="Bundesliga", country="Germany"),
        Competition(id=5, sorare_id="comp_sa", slug="serie-a", name="Serie A", country="Italy"),
        Competition(id=6, sorare_id="comp_l1", slug="ligue-1", name="Ligue 1", country="France"),
    ]
    session.add_all(comps)
    await session.flush()

    # 3. Clubs
    clubs_data = [
        (1, "real-madrid", "Real Madrid", "RMA", "https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=128", "Spain"),
        (2, "manchester-city", "Manchester City", "MCI", "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=128", "England"),
        (3, "arsenal", "Arsenal", "ARS", "https://images.unsplash.com/photo-1489944445301-ff510f8699ae?w=128", "England"),
        (4, "bayern-munich", "Bayern Munich", "BAY", "https://images.unsplash.com/photo-1518091043644-c1d4457512c6?w=128", "Germany"),
        (5, "paris-saint-germain", "Paris Saint-Germain", "PSG", "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=128", "France"),
        (6, "barcelona", "Barcelona", "FCB", "https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=128", "Spain"),
        (7, "inter-milan", "Inter Milan", "INT", "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=128", "Italy"),
        (8, "liverpool", "Liverpool", "LIV", "https://images.unsplash.com/photo-1489944445301-ff510f8699ae?w=128", "England"),
        (9, "bayer-leverkusen", "Bayer Leverkusen", "B04", "https://images.unsplash.com/photo-1518091043644-c1d4457512c6?w=128", "Germany"),
        (10, "atletico-madrid", "Atletico Madrid", "ATM", "https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=128", "Spain"),
    ]
    clubs = [
        Club(id=cid, sorare_id=f"club_{slug}", slug=slug, name=cname, short_name=sname, logo_url=lurl, country=cnt)
        for cid, slug, cname, sname, lurl, cnt in clubs_data
    ]
    session.add_all(clubs)
    await session.flush()

    # 4. SO5 Fixtures (Gameweeks)
    so5_fixtures = [
        SO5Fixture(
            id=1,
            sorare_id="gw_501",
            event="football",
            event_name="Champion Europe",
            event_type="classic",
            game_week=501,
            start_date=now - timedelta(days=7),
            end_date=now - timedelta(days=3),
            cutoff_date=now - timedelta(days=7, hours=2),
            state="closed",
        ),
        SO5Fixture(
            id=2,
            sorare_id="gw_502",
            event="football",
            event_name="Champion Europe & All-Star",
            event_type="classic",
            game_week=502,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=3),
            cutoff_date=now - timedelta(days=1, hours=2),
            state="opened",
        ),
        SO5Fixture(
            id=3,
            sorare_id="gw_503",
            event="football",
            event_name="Challenger & Underdog",
            event_type="classic",
            game_week=503,
            start_date=now + timedelta(days=4),
            end_date=now + timedelta(days=8),
            cutoff_date=now + timedelta(days=4, hours=2),
            state="upcoming",
        ),
    ]
    session.add_all(so5_fixtures)
    await session.flush()

    # 5. Games
    games_data = [
        (1, 1, 6, 2, now - timedelta(days=4), "PLAYED", 2, 1, 90), # Real vs Barca
        (2, 2, 3, 1, now - timedelta(days=3), "PLAYED", 2, 2, 90), # Man City vs Arsenal
        (3, 4, 9, 4, now - timedelta(days=3), "PLAYED", 1, 1, 90), # Bayern vs Leverkusen
        (4, 7, 10, 3, now + timedelta(days=1), "SCHEDULED", None, None, None), # Inter vs Atletico
        (5, 8, 2, 1, now + timedelta(days=2), "SCHEDULED", None, None, None), # Liverpool vs Man City
        (6, 1, 5, 3, now + timedelta(days=2), "SCHEDULED", None, None, None), # Real vs PSG
        (7, 3, 8, 1, now + timedelta(days=6), "SCHEDULED", None, None, None), # Arsenal vs Liverpool
        (8, 6, 10, 2, now + timedelta(days=7), "SCHEDULED", None, None, None), # Barca vs Atletico
    ]
    games = [
        Game(
            id=gid,
            sorare_id=f"game_{gid}",
            home_club_id=hc,
            away_club_id=ac,
            competition_id=comp,
            date=gdate,
            status=st,
            home_score=hs,
            away_score=as_,
            minute=min_,
            coverage_status="FULL",
        )
        for gid, hc, ac, comp, gdate, st, hs, as_, min_ in games_data
    ]
    session.add_all(games)
    await session.flush()

    # 6. Players (52 realistic European players across all positions)
    raw_players = [
        # Goalkeepers
        (1, "thibaut-courtois", "Thibaut Courtois", "Thibaut", "Courtois", 32, "Goalkeeper", 1, "Belgium", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", 85.0),
        (2, "ederson-moraes", "Ederson", "Ederson", "Moraes", 31, "Goalkeeper", 2, "Brazil", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", 62.0),
        (3, "david-raya", "David Raya", "David", "Raya", 29, "Goalkeeper", 3, "Spain", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150", 55.0),
        (4, "manuel-neuer", "Manuel Neuer", "Manuel", "Neuer", 38, "Goalkeeper", 4, "Germany", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150", 48.0),
        (5, "gianluigi-donnarumma", "Gianluigi Donnarumma", "Gianluigi", "Donnarumma", 25, "Goalkeeper", 5, "Italy", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150", 72.0),
        (6, "marc-andre-ter-stegen", "Marc-André ter Stegen", "Marc-André", "ter Stegen", 32, "Goalkeeper", 6, "Germany", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", 40.0),
        (7, "yann-sommer", "Yann Sommer", "Yann", "Sommer", 35, "Goalkeeper", 7, "Switzerland", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150", 38.0),
        (8, "alisson-becker", "Alisson Becker", "Alisson", "Becker", 32, "Goalkeeper", 8, "Brazil", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150", 68.0),

        # Defenders
        (9, "william-saliba", "William Saliba", "William", "Saliba", 23, "Defender", 3, "France", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", 82.0),
        (10, "gabriel-magalhaes", "Gabriel Magalhães", "Gabriel", "Magalhães", 26, "Defender", 3, "Brazil", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", 54.0),
        (11, "virgil-van-dijk", "Virgil van Dijk", "Virgil", "van Dijk", 33, "Defender", 8, "Netherlands", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", 78.0),
        (12, "antonio-rudiger", "Antonio Rüdiger", "Antonio", "Rüdiger", 31, "Defender", 1, "Germany", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150", 65.0),
        (13, "ruben-dias", "Rúben Dias", "Rúben", "Dias", 27, "Defender", 2, "Portugal", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150", 70.0),
        (14, "josko-gvardiol", "Josko Gvardiol", "Josko", "Gvardiol", 22, "Defender", 2, "Croatia", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150", 88.0),
        (15, "alphonso-davies", "Alphonso Davies", "Alphonso", "Davies", 24, "Defender", 4, "Canada", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", 60.0),
        (16, "trent-alexander-arnold", "Trent Alexander-Arnold", "Trent", "Alexander-Arnold", 26, "Defender", 8, "England", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", 92.0),
        (17, "jules-kounde", "Jules Koundé", "Jules", "Koundé", 26, "Defender", 6, "France", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", 52.0),
        (18, "alessandro-bastoni", "Alessandro Bastoni", "Alessandro", "Bastoni", 25, "Defender", 7, "Italy", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150", 64.0),
        (19, "jeremie-frimpong", "Jeremie Frimpong", "Jeremie", "Frimpong", 23, "Defender", 9, "Netherlands", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150", 75.0),
        (20, "achraf-hakimi", "Achraf Hakimi", "Achraf", "Hakimi", 26, "Defender", 5, "Morocco", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150", 80.0),
        (21, "federico-dimarco", "Federico Dimarco", "Federico", "Dimarco", 27, "Defender", 7, "Italy", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", 67.0),
        (22, "dayot-upamecano", "Dayot Upamecano", "Dayot", "Upamecano", 26, "Defender", 4, "France", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", 45.0),

        # Midfielders
        (23, "jude-bellingham", "Jude Bellingham", "Jude", "Bellingham", 21, "Midfielder", 1, "England", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", 220.0),
        (24, "kevin-de-bruyne", "Kevin De Bruyne", "Kevin", "De Bruyne", 33, "Midfielder", 2, "Belgium", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150", 110.0),
        (25, "rodri-hernandez", "Rodri", "Rodrigo", "Hernández", 28, "Midfielder", 2, "Spain", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150", 95.0),
        (26, "martin-odegaard", "Martin Ødegaard", "Martin", "Ødegaard", 25, "Midfielder", 3, "Norway", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150", 125.0),
        (27, "declan-rice", "Declan Rice", "Declan", "Rice", 25, "Midfielder", 3, "England", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", 88.0),
        (28, "jamal-musiala", "Jamal Musiala", "Jamal", "Musiala", 21, "Midfielder", 4, "Germany", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", 160.0),
        (29, "pedri-gonzalez", "Pedri", "Pedro", "González", 22, "Midfielder", 6, "Spain", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", 115.0),
        (30, "federico-valverde", "Federico Valverde", "Federico", "Valverde", 26, "Midfielder", 1, "Uruguay", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150", 140.0),
        (31, "florian-wirtz", "Florian Wirtz", "Florian", "Wirtz", 21, "Midfielder", 9, "Germany", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150", 185.0),
        (32, "nicolo-barella", "Nicolò Barella", "Nicolò", "Barella", 27, "Midfielder", 7, "Italy", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150", 75.0),
        (33, "eduardo-camavinga", "Eduardo Camavinga", "Eduardo", "Camavinga", 22, "Midfielder", 1, "France", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", 90.0),
        (34, "phil-foden", "Phil Foden", "Phil", "Foden", 24, "Midfielder", 2, "England", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", 155.0),
        (35, "gavi-paez", "Gavi", "Pablo", "Páez", 20, "Midfielder", 6, "Spain", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", 80.0),
        (36, "vitinha-machado", "Vitinha", "Vítor", "Machado", 24, "Midfielder", 5, "Portugal", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150", 70.0),
        (37, "alexis-mac-allister", "Alexis Mac Allister", "Alexis", "Mac Allister", 25, "Midfielder", 8, "Argentina", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150", 82.0),
        (38, "granit-xhaka", "Granit Xhaka", "Granit", "Xhaka", 32, "Midfielder", 9, "Switzerland", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150", 42.0),

        # Forwards
        (39, "kylian-mbappe", "Kylian Mbappé", "Kylian", "Mbappé", 25, "Forward", 1, "France", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", 280.0),
        (40, "erling-haaland", "Erling Haaland", "Erling", "Haaland", 24, "Forward", 2, "Norway", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", 295.0),
        (41, "vinicius-junior", "Vinícius Jr.", "Vinícius", "Júnior", 24, "Forward", 1, "Brazil", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", 260.0),
        (42, "bukayo-saka", "Bukayo Saka", "Bukayo", "Saka", 23, "Forward", 3, "England", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150", 190.0),
        (43, "harry-kane", "Harry Kane", "Harry", "Kane", 31, "Forward", 4, "England", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150", 210.0),
        (44, "mohamed-salah", "Mohamed Salah", "Mohamed", "Salah", 32, "Forward", 8, "Egypt", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150", 175.0),
        (45, "lamine-yamal", "Lamine Yamal", "Lamine", "Yamal", 17, "Forward", 6, "Spain", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", 250.0),
        (46, "robert-lewandowski", "Robert Lewandowski", "Robert", "Lewandowski", 36, "Forward", 6, "Poland", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", 95.0),
        (47, "lautaro-martinez", "Lautaro Martínez", "Lautaro", "Martínez", 27, "Forward", 7, "Argentina", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", 130.0),
        (48, "rodrygo-silva", "Rodrygo", "Rodrygo", "Silva", 23, "Forward", 1, "Brazil", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150", 120.0),
        (49, "cole-palmer", "Cole Palmer", "Cole", "Palmer", 22, "Forward", 3, "England", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150", 170.0),
        (50, "ousmane-dembele", "Ousmane Dembélé", "Ousmane", "Dembélé", 27, "Forward", 5, "France", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150", 85.0),
        (51, "kai-havertz", "Kai Havertz", "Kai", "Havertz", 25, "Forward", 3, "Germany", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", 90.0),
        (52, "victor-osimhen", "Victor Osimhen", "Victor", "Osimhen", 25, "Forward", 5, "Nigeria", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", 145.0),
    ]

    players_list = []
    for pid, slug, dname, fname, lname, age, pos, club_id, nat, img, base_price in raw_players:
        p = Player(
            id=pid,
            sorare_id=f"player_{slug}",
            slug=slug,
            display_name=dname,
            first_name=fname,
            last_name=lname,
            age=age,
            position=pos,
            active_club_id=club_id,
            nationality=nat,
            image_url=img,
        )
        players_list.append(p)
    session.add_all(players_list)
    await session.flush()

    # 7. Injuries & Suspensions
    # Rodri is injured (ACL)
    inj_rodri = Injury(
        id=1,
        player_id=25,
        sorare_id="inj_rodri",
        active=True,
        kind="ACL Knee Tear",
        details="Underwent knee ligament surgery, ruled out for extended period.",
        status="OUT",
        start_date=now - timedelta(days=20),
        expected_end_date=now + timedelta(days=180),
    )
    # De Bruyne managing slight groin tightness
    inj_kdb = Injury(
        id=2,
        player_id=24,
        sorare_id="inj_kdb",
        active=True,
        kind="Groin Strain",
        details="Evaluating match fitness in final training session.",
        status="DOUBTFUL",
        start_date=now - timedelta(days=4),
        expected_end_date=now + timedelta(days=5),
    )
    # Rudiger serving red card suspension
    susp_rudiger = Suspension(
        id=1,
        player_id=12,
        sorare_id="susp_rudiger",
        active=True,
        competition="La Liga",
        kind="Red Card Disciplinary",
        reason="Two yellow card accumulation in previous match.",
        start_date=now - timedelta(days=3),
        end_date=now + timedelta(days=4),
        matches=1,
    )
    session.add_all([inj_rodri, inj_kdb, susp_rudiger])
    await session.flush()

    # 8. Scores, Cards, Prices & Metrics for each player
    import random

    # Fix random seed for reproducible realistic values
    rng = random.Random(42)

    for p, raw in zip(players_list, raw_players):
        base_price = raw[10]
        # Generate 5 recent match scores
        scores_vals = []
        for i in range(5):
            # Star players average 60-85, regular starters 45-65
            sc = min(100.0, max(20.0, rng.gauss(65.0, 14.0)))
            scores_vals.append(round(sc, 1))

            score_obj = PlayerGameScore(
                player_id=p.id,
                game_id=(i % len(games)) + 1,
                score=round(sc, 1),
                average_score=62.0,
                projected_score=round(sc * 0.95, 1),
                projection_grade="A" if sc > 65 else "B",
                projection_reliability=85.0,
                decisive_score=35.0 if sc > 60 else 0.0,
                all_around_score=round(sc - 35.0, 1) if sc > 60 else round(sc, 1),
                score_status="FINAL",
                scoring_version="v2",
                created_at=now - timedelta(days=(i * 4) + 1),
            )
            session.add(score_obj)

        # Generate Limited and Rare Cards
        for rarity, multiplier in [("limited", 1.0), ("rare", 4.5)]:
            card = Card(
                player_id=p.id,
                sorare_id=f"card_{p.slug}_{rarity}_2024",
                asset_id=f"asset_{p.id}_{rarity}",
                season_year=2024,
                rarity=rarity,
                position=p.position,
                power=round(rng.uniform(10.0, 45.0), 1),
                grade="MINT",
                image_url=p.image_url,
            )
            session.add(card)
            await session.flush()

            # Card Prices & Snapshots
            curr_price = round(base_price * multiplier, 2)
            price_rec = CardPrice(
                card_id=card.id,
                price=curr_price,
                currency="EUR",
                source="secondary_market",
                observed_at=now - timedelta(hours=2),
            )
            session.add(price_rec)

            # Snapshot
            snapshot = PriceSnapshot(
                player_id=p.id,
                card_id=card.id,
                average_price=curr_price,
                lowest_ask=round(curr_price * 0.98, 2),
                highest_bid=round(curr_price * 0.92, 2),
                volume_24h=round(curr_price * 3.5, 2),
                currency="EUR",
                observed_at=now - timedelta(days=1),
            )
            session.add(snapshot)

        # Compute Analytics & Metric Record
        is_inj = (p.id in {24, 25})
        inj_st = "OUT" if p.id == 25 else ("DOUBTFUL" if p.id == 24 else None)
        inj_kd = "ACL" if p.id == 25 else ("Groin" if p.id == 24 else None)
        is_susp = (p.id == 12)
        susp_rs = "Red Card" if p.id == 12 else None

        intel = AnalyticsEngine.compute_player_intelligence(
            player_id=p.id,
            recent_scores=scores_vals,
            recent_minutes=[90, 90, 85, 90, 90],
            recent_starts=5,
            is_injured=is_inj,
            injury_kind=inj_kd,
            injury_status=inj_st,
            is_suspended=is_susp,
            suspension_reason=susp_rs,
            current_price=base_price,
            avg_30d_price=round(base_price * 1.05, 2),
        )

        metric_row = PlayerMetric(
            player_id=p.id,
            form_score=intel.form_score,
            consistency_score=intel.consistency_score,
            minutes_score=intel.minutes_score,
            fixture_score=intel.fixture_score,
            market_score=intel.market_score,
            availability_score=intel.availability_score,
            scout_score=intel.scout_score,
            risk_score=intel.risk_score,
            risk_level=intel.risk_level.value,
            starting_probability=intel.starting_probability,
            recommendation=intel.recommendation.value,
            confidence=intel.confidence,
            calculated_at=now,
        )
        session.add(metric_row)

    await session.flush()

    # 9. News linked to players
    news_items = [
        (
            "Kylian Mbappé hits decisive form ahead of European clash",
            "https://scoutlab.io/news/mbappe-form",
            "ScoutLab Tactical Desk",
            "tactical",
            "Mbappé has generated 4 decisive scoring actions over his last three starts, showcasing exceptional expected goals conversion.",
            [39],
        ),
        (
            "Erling Haaland match conditioning update: 100% fit for upcoming fixtures",
            "https://scoutlab.io/news/haaland-fit",
            "Premier Intelligence",
            "match_report",
            "Medical staff confirm Erling Haaland trained without restriction and is expected to lead the attack.",
            [40],
        ),
        (
            "Rodri ACL surgery recovery timeline and midfield impact analysis",
            "https://scoutlab.io/news/rodri-injury",
            "Medical Scout",
            "injury",
            "Confirmed absence of Rodri leaves a substantial gap in central possession dominance for Manchester City.",
            [25],
        ),
        (
            "Jude Bellingham returns to central attacking role with enhanced box arrivals",
            "https://scoutlab.io/news/bellingham-role",
            "La Liga Scouting Reports",
            "tactical",
            "Tactical analysis highlights Jude Bellingham operating higher up the pitch with increased shots inside the penalty box.",
            [23],
        ),
        (
            "William Saliba defensive consistency reaches record high SO5 metrics",
            "https://scoutlab.io/news/saliba-record",
            "Opta / ScoutLab Analytics",
            "general",
            "Saliba leads all European defenders in duels won without committing fouls, bolstering clean sheet consistency.",
            [9],
        ),
    ]

    for n_title, n_url, n_src, n_cat, n_sum, linked_pids in news_items:
        news_obj = News(
            title=n_title,
            url=n_url,
            source=n_src,
            category=n_cat,
            summary=n_sum,
            source_type="REPORT",
            published_at=now - timedelta(hours=random.randint(2, 48)),
        )
        session.add(news_obj)
        await session.flush()

        for pid in linked_pids:
            link = NewsPlayerLink(news_id=news_obj.id, player_id=pid)
            session.add(link)

    # 10. Watchlists & Alerts for user1
    wl1 = Watchlist(user_id=1, player_id=39, target_price=260.0, notes="Target entry when floor dips below 260 EUR")
    wl2 = Watchlist(user_id=1, player_id=23, target_price=200.0, notes="Top priority midfielder for Champion Europe lineup")
    wl3 = Watchlist(user_id=1, player_id=45, target_price=220.0, notes="Lamine Yamal high upside growth hold")
    session.add_all([wl1, wl2, wl3])

    alerts_data = [
        (1, 39, "PRICE_DROP", "Mbappé Floor Price Drop Detected", "Kylian Mbappé limited card floor dropped 6.2% to 262 EUR.", "INFO", "FACT"),
        (1, 25, "INJURY_UPDATE", "Rodri Medical Alert: Confirmed Out", "Rodri is confirmed out following knee surgery. Sell / bench advised.", "CRITICAL", "FACT"),
        (1, 40, "STARTING_XI", "Starting XI Prediction: Haaland Starter (95%)", "Erling Haaland confirmed in pre-match expected lineups.", "SUCCESS", "PREDICTION"),
        (1, 24, "INJURY_UPDATE", "Kevin De Bruyne Doubtful for Next Match", "Managing groin tightness; late fitness test scheduled.", "WARNING", "REPORT"),
    ]
    for uid, pid, atype, atitle, amsg, asev, asrc in alerts_data:
        session.add(
            Alert(
                user_id=uid,
                player_id=pid,
                type=atype,
                title=atitle,
                message=amsg,
                severity=asev,
                source_type=asrc,
                read=False,
                created_at=now - timedelta(hours=random.randint(1, 12)),
            )
        )

    # 11. Initial Sync Status
    sync_jobs = [
        "sync_players",
        "sync_clubs",
        "sync_competitions",
        "sync_games",
        "sync_player_scores",
        "sync_injuries",
        "sync_suspensions",
        "sync_cards",
        "sync_market",
        "sync_so5_fixtures",
    ]
    for jname in sync_jobs:
        session.add(
            SyncStatus(
                job_name=jname,
                status="SUCCESS",
                last_started_at=now - timedelta(minutes=15),
                last_finished_at=now - timedelta(minutes=14),
                records_processed=50,
            )
        )

    await session.commit()
    logger.info("ScoutLab seed data successfully created: 52 players, clubs, cards, intelligence metrics & alerts.")


if __name__ == "__main__":
    asyncio.run(seed_database())
