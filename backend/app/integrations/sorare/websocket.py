import asyncio
import json
import logging
from typing import Callable, Dict, List, Optional
import websockets
from app.config import settings
from app.utils.redis_client import cache

logger = logging.getLogger(__name__)


class SorareWebSocketClient:
    """ActionCable / WebSocket client for real-time Sorare subscriptions.
    
    Subscribes to live entity updates and handles cache invalidation.
    """

    SUBSCRIPTIONS = [
        "anyCardWasUpdated",
        "anyGameWasUpdated",
        "gameWasUpdated",
        "tokenAuctionWasUpdated",
        "tokenOfferWasUpdated",
        "primaryOfferWasUpdated",
    ]

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
        on_event: Optional[Callable[[str, Dict], None]] = None,
    ):
        self.url = url or settings.SORARE_WS_URL
        self.api_key = api_key or settings.SORARE_API_KEY
        self.jwt_token = jwt_token or settings.SORARE_JWT
        self.on_event = on_event
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start WebSocket listener in a background task."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._listen_loop())
        logger.info("Sorare WebSocket worker started.")

    async def stop(self) -> None:
        """Stop WebSocket listener."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Sorare WebSocket worker stopped.")

    async def _listen_loop(self) -> None:
        backoff = 2
        while self._running:
            if not self.url or (not self.api_key and not self.jwt_token and not settings.DEMO_MODE):
                logger.info("Sorare WebSocket not configured or in DEMO_MODE; listener idling.")
                await asyncio.sleep(60)
                continue

            try:
                headers = {}
                if self.api_key:
                    headers["APIKEY"] = self.api_key
                if self.jwt_token:
                    headers["Authorization"] = f"Bearer {self.jwt_token}"
                    headers["JWT-AUD"] = "scoutlab" 

                logger.info(f"Connecting to Sorare WebSocket at {self.url}...")
                async with websockets.connect(self.url, additional_headers=headers) as ws:
                    logger.info("Connected to Sorare WebSocket.")
                    backoff = 2  # Reset backoff on successful connect

                    # Subscribe to ActionCable channels
                    for event_name in self.SUBSCRIPTIONS:
                        sub_msg = {
                            "command": "subscribe",
                            "identifier": json.dumps({"channel": "GraphqlChannel"}),
                            "data": json.dumps({"action": "subscribe", "event": event_name}),
                        }
                        await ws.send(json.dumps(sub_msg))

                    while self._running:
                        message = await ws.recv()
                        await self._process_message(message)

            except (websockets.ConnectionClosed, OSError, Exception) as exc:
                if not self._running:
                    break
                logger.warning(
                    f"Sorare WebSocket disconnected ({exc.__class__.__name__}). Reconnecting in {backoff}s..."
                )
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)

    async def _process_message(self, raw_message: str) -> None:
        try:
            data = json.loads(raw_message)
            msg_type = data.get("type")
            if msg_type in {"ping", "welcome"}:
                return

            message = data.get("message", {})
            event_type = message.get("event")
            payload = message.get("data", {})

            if event_type:
                logger.info(f"Received Sorare event: {event_type}")
                await self._handle_event(event_type, payload)

        except Exception as e:
            logger.error(f"Error processing Sorare WebSocket message: {e}")

    async def _handle_event(self, event_type: str, payload: Dict) -> None:
        """Invalidate affected Redis cache keys and notify subscribers."""
        if "Card" in event_type or "Offer" in event_type or "Auction" in event_type:
            await cache.delete_prefix("market:")
            await cache.delete_prefix("players:list:")
            card_id = payload.get("id")
            if card_id:
                await cache.delete(f"card:{card_id}")

        elif "Game" in event_type:
            await cache.delete_prefix("fixture:")
            await cache.delete_prefix("dashboard:")

        if self.on_event:
            try:
                self.on_event(event_type, payload)
            except Exception as e:
                logger.warning(f"Error in on_event callback: {e}")


sorare_ws_client = SorareWebSocketClient()


