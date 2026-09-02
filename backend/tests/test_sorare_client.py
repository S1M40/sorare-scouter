import pytest
from unittest.mock import AsyncMock, patch
import httpx
from app.integrations.sorare.client import SorareGraphQLClient


@pytest.mark.asyncio
async def test_sorare_client_success():
    client = SorareGraphQLClient(endpoint="https://api.sorare.mock/graphql", api_key="test_key")

    mock_response = httpx.Response(
        200,
        json={
            "data": {
                "football": {
                    "player": {
                        "id": "p_1",
                        "slug": "kylian-mbappe",
                        "displayName": "Kylian Mbappé",
                    }
                }
            }
        },
        request=httpx.Request("POST", "https://api.sorare.mock/graphql"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        player = await client.get_player_by_slug("kylian-mbappe")
        assert player is not None
        assert player["slug"] == "kylian-mbappe"
        assert player["displayName"] == "Kylian Mbappé"


@pytest.mark.asyncio
async def test_sorare_client_graphql_error():
    client = SorareGraphQLClient(endpoint="https://api.sorare.mock/graphql")

    mock_response = httpx.Response(
        200,
        json={"errors": [{"message": "Field 'invalid' does not exist"}]},
        request=httpx.Request("POST", "https://api.sorare.mock/graphql"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await client.execute_query("query { invalid }", cache_ttl=0)
        assert result is None


@pytest.mark.asyncio
async def test_sorare_client_network_timeout():
    client = SorareGraphQLClient(endpoint="https://api.sorare.mock/graphql", max_retries=2)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.ConnectTimeout("Connection timed out")
        result = await client.execute_query("query { test }", cache_ttl=0)
        assert result is None
        assert mock_post.call_count == 2
