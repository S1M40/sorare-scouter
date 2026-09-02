import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.seed import seed_database


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient, db_session: AsyncSession):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"healthy", "degraded"}
    assert "database" in data
    assert "redis" in data


@pytest.mark.asyncio
async def test_dashboard_and_players_api(client: AsyncClient, db_session: AsyncSession):
    # Ensure seed data is populated
    await seed_database(db_session)

    # 1. Dashboard
    dash_resp = await client.get("/api/v1/dashboard")
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert "data" in dash_data
    assert "meta" in dash_data
    assert "players_in_form" in dash_data["data"]
    assert "current_gameweek" in dash_data["data"]
    assert dash_data["meta"]["source"] == "scoutlab"

    # 2. Players List
    players_resp = await client.get("/api/v1/players?page=1&page_size=10")
    assert players_resp.status_code == 200
    players_data = players_resp.json()
    assert "data" in players_data
    assert "meta" in players_data
    assert len(players_data["data"]) == 10
    assert players_data["meta"]["total"] >= 50
    assert players_data["meta"]["page"] == 1

    # 3. Player Filters (Position and Search)
    filter_resp = await client.get("/api/v1/players?position=Forward&search=Mbappé")
    assert filter_resp.status_code == 200
    filter_data = filter_resp.json()
    assert len(filter_data["data"]) >= 1
    assert "Mbappé" in filter_data["data"][0]["display_name"]
    first_player_id = filter_data["data"][0]["id"]

    # 4. Player Details
    profile_resp = await client.get(f"/api/v1/players/{first_player_id}")
    assert profile_resp.status_code == 200
    profile_data = profile_resp.json()["data"]
    assert profile_data["display_name"] == "Kylian Mbappé"
    assert "metric" in profile_data
    assert profile_data["metric"]["starting_prediction"]["label"] == "PREDICTION"

    # 5. Player Sub-endpoints
    scores_resp = await client.get(f"/api/v1/players/{first_player_id}/scores")
    assert scores_resp.status_code == 200

    fixtures_resp = await client.get(f"/api/v1/players/{first_player_id}/fixtures")
    assert fixtures_resp.status_code == 200

    market_resp = await client.get(f"/api/v1/players/{first_player_id}/market")
    assert market_resp.status_code == 200


@pytest.mark.asyncio
async def test_market_and_fixtures_api(client: AsyncClient, db_session: AsyncSession):
    await seed_database(db_session)

    # Market Overview
    m_resp = await client.get("/api/v1/market")
    assert m_resp.status_code == 200
    assert "top_gainers" in m_resp.json()["data"]

    # Market Movers
    movers_resp = await client.get("/api/v1/market/movers?limit=5")
    assert movers_resp.status_code == 200
    assert len(movers_resp.json()["data"]) <= 5

    # Fixtures
    fix_resp = await client.get("/api/v1/fixtures")
    assert fix_resp.status_code == 200
    assert "meta" in fix_resp.json()

    # Gameweeks
    gw_resp = await client.get("/api/v1/fixtures/gameweeks")
    assert gw_resp.status_code == 200
    assert len(gw_resp.json()["data"]) >= 1

    # Group
    grp_resp = await client.get("/api/v1/group/ranking")
    assert grp_resp.status_code == 200
    assert "rankings" in grp_resp.json()["data"]
