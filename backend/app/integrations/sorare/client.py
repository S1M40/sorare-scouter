import asyncio
import logging
from typing import Any, Dict, List, Optional
import httpx
from app.config import settings
from app.utils.redis_client import cache
from app.integrations.base import SorareProvider
from app.integrations.sorare.queries import (
    GET_PLAYER_BY_SLUG_QUERY,
    GET_PLAYERS_PAGINATED_QUERY,
    GET_CARDS_BY_PLAYER_QUERY,
    GET_SO5_FIXTURES_QUERY,
    GET_ACTIVE_AUCTIONS_QUERY,
)

logger = logging.getLogger(__name__)


class SorareGraphQLClient(SorareProvider):
    """Production GraphQL client for the official Sorare API.
    
    Includes cursor pagination, exponential backoff retries, request timeouts,
    structured error logging, and Redis response caching.
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
        timeout: float = 12.0,
        max_retries: int = 3,
    ):
        self.endpoint = endpoint or settings.SORARE_GRAPHQL_URL
        self.api_key = api_key or settings.SORARE_API_KEY
        self.jwt_token = jwt_token or settings.SORARE_JWT
        self.timeout = timeout
        self.max_retries = max_retries

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ScoutLab-Backend/1.0",
        }
        if self.api_key:
            headers["APIKEY"] = self.api_key
        if self.jwt_token:
            headers['Authorization'] = f'Bearer {self.jwt_token}'
            headers['JWT-AUD'] = 'scoutlab'
        return headers

    async def execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        cache_ttl: Optional[int] = 300,
    ) -> Optional[Dict[str, Any]]:
        """Execute a GraphQL query with retries, backoff, and caching."""
        # 1. Check cache if key can be derived
        cache_key = None
        if cache_ttl and cache_ttl > 0:
            import hashlib
            query_hash = hashlib.md5(f"{query}:{variables}".encode("utf-8")).hexdigest()
            cache_key = f"sorare:gql:{query_hash}"
            cached_val = await cache.get(cache_key)
            if cached_val:
                return cached_val

        # 2. Check if credentials/URL are configured
        if not self.endpoint:
            logger.warning("Sorare GraphQL endpoint is not configured.")
            return None

        payload = {"query": query, "variables": variables or {}}
        headers = self._get_headers()

        # 3. Retry loop with exponential backoff
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(self.endpoint, json=payload, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    if "errors" in data:
                        logger.error(f"Sorare GraphQL query errors: {data['errors']}")
                        return None
                    
                    result = data.get("data")
                    if cache_key and result:
                        await cache.set(cache_key, result, ttl=cache_ttl)
                    return result

                elif response.status_code in {429, 500, 502, 503, 504}:
                    backoff = (2 ** attempt) * 0.5
                    logger.warning(
                        f"Sorare API returned HTTP {response.status_code}. Retrying in {backoff:.1f}s (attempt {attempt}/{self.max_retries})"
                    )
                    await asyncio.sleep(backoff)
                else:
                    logger.error(f"Sorare API returned HTTP {response.status_code}: {response.text}")
                    return None

            except (httpx.RequestError, httpx.TimeoutException) as exc:
                backoff = (2 ** attempt) * 0.5
                logger.warning(
                    f"Sorare request error ({exc.__class__.__name__}): {exc}. Retrying in {backoff:.1f}s (attempt {attempt}/{self.max_retries})"
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(backoff)
                else:
                    logger.error(f"Failed to connect to Sorare API after {self.max_retries} attempts.")
                    return None

        return None

    async def get_player_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Retrieve single player details by slug."""
        data = await self.execute_query(
            GET_PLAYER_BY_SLUG_QUERY, variables={"slug": slug}, cache_ttl=600
        )
        if data and "football" in data and "player" in data["football"]:
            return data["football"]["player"]
        return None

    async def get_players_paginated(
        self, first: int = 50, after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch players page using GraphQL cursor pagination."""
        data = await self.execute_query(
            GET_PLAYERS_PAGINATED_QUERY,
            variables={"first": first, "after": after},
            cache_ttl=300,
        )
        if data and "football" in data and "players" in data["football"]:
            return data["football"]["players"]
        return {"nodes": [], "pageInfo": {"hasNextPage": False, "endCursor": None}}

    async def get_cards(self, slug: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve cards for a player slug."""
        data = await self.execute_query(
            GET_CARDS_BY_PLAYER_QUERY,
            variables={"slug": slug, "first": limit},
            cache_ttl=300,
        )
        if data and "football" in data and data["football"].get("player"):
            cards_obj = data["football"]["player"].get("cards", {})
            return cards_obj.get("nodes", [])
        return []

    async def get_so5_fixtures(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve upcoming and live SO5 fixtures."""
        data = await self.execute_query(GET_SO5_FIXTURES_QUERY, cache_ttl=600)
        if data and "football" in data and "so5Fixtures" in data["football"]:
            return data["football"]["so5Fixtures"][:limit]
        return []

    async def get_active_auctions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve live auctions on the primary market."""
        data = await self.execute_query(
            GET_ACTIVE_AUCTIONS_QUERY, variables={"first": limit}, cache_ttl=60
        )
        if data and "football" in data and "tokenAuctions" in data["football"]:
            return data["football"]["tokenAuctions"].get("nodes", [])
        return []


sorare_client = SorareGraphQLClient()
