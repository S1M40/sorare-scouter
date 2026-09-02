import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.seed import seed_database


@pytest.mark.asyncio
async def test_auth_and_protected_routes(client: AsyncClient, db_session: AsyncSession):
    await seed_database(db_session)

    # 1. Register new user
    reg_payload = {
        "username": "new_scout_user",
        "email": "newuser@scoutlab.io",
        "password": "strongPassword123",
        "group_name": "ScoutLab Alpha Syndicate",
    }
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 200
    user_data = reg_resp.json()["data"]
    assert user_data["username"] == "new_scout_user"

    # 2. Login
    login_payload = {
        "email_or_username": "newuser@scoutlab.io",
        "password": "strongPassword123",
    }
    login_resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    token_data = login_resp.json()["data"]
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Access /auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["data"]["email"] == "newuser@scoutlab.io"

    # 4. Watchlist addition and removal
    add_wl_resp = await client.post(
        "/api/v1/watchlist/1",
        json={"target_price": 50.0, "notes": "Must buy under 50 EUR"},
        headers=headers,
    )
    assert add_wl_resp.status_code == 200

    get_wl_resp = await client.get("/api/v1/watchlist", headers=headers)
    assert get_wl_resp.status_code == 200
    assert len(get_wl_resp.json()["data"]) >= 1

    del_wl_resp = await client.delete("/api/v1/watchlist/1", headers=headers)
    assert del_wl_resp.status_code == 200

    # 5. Alerts
    alerts_resp = await client.get("/api/v1/alerts", headers=headers)
    assert alerts_resp.status_code == 200
