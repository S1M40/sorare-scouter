from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class SorareProvider(ABC):
    """Abstract interface for Sorare data retrieval."""

    @abstractmethod
    async def get_player_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_cards(self, slug: str, limit: int = 10) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_so5_fixtures(self, limit: int = 10) -> List[Dict[str, Any]]:
        pass


class NewsProvider(ABC):
    """Abstract interface for external football news integration."""

    @abstractmethod
    async def fetch_latest_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        pass


class PredictionProvider(ABC):
    """Abstract interface for starting XI and match predictions (enables future ML models)."""

    @abstractmethod
    async def predict_starting_xi(self, player_id: int) -> Dict[str, Any]:
        pass
