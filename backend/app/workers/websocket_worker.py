import logging
from app.integrations.sorare.websocket import sorare_ws_client

logger = logging.getLogger(__name__)


async def start_websocket_worker() -> None:
    logger.info("Initializing Sorare WebSocket subscriber...")
    await sorare_ws_client.start()


async def stop_websocket_worker() -> None:
    logger.info("Stopping Sorare WebSocket subscriber...")
    await sorare_ws_client.stop()
