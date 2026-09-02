from app.integrations.sorare.queries.players import (
    GET_PLAYER_BY_SLUG_QUERY,
    GET_PLAYERS_PAGINATED_QUERY,
)
from app.integrations.sorare.queries.cards import (
    GET_CARDS_BY_PLAYER_QUERY,
    GET_CARD_BY_ID_QUERY,
)
from app.integrations.sorare.queries.fixtures import (
    GET_SO5_FIXTURES_QUERY,
    GET_GAMES_BY_DATE_QUERY,
)
from app.integrations.sorare.queries.market import GET_ACTIVE_AUCTIONS_QUERY

__all__ = [
    "GET_PLAYER_BY_SLUG_QUERY",
    "GET_PLAYERS_PAGINATED_QUERY",
    "GET_CARDS_BY_PLAYER_QUERY",
    "GET_CARD_BY_ID_QUERY",
    "GET_SO5_FIXTURES_QUERY",
    "GET_GAMES_BY_DATE_QUERY",
    "GET_ACTIVE_AUCTIONS_QUERY",
]
