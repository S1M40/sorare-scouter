import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import init_db
from app.utils.redis_client import cache
from app.utils.logger import logger
from app.api.endpoints.health import router as health_router
from app.api.router import api_router
from app.workers.sync_worker import sync_worker
from app.workers.websocket_worker import start_websocket_worker, stop_websocket_worker
from app.utils.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown event lifecycle."""
    logger.info("Initializing ScoutLab Backend...")

    # 1. Connect Redis
    await cache.connect()

    # 2. Verify / Initialize Database Tables
    await init_db()

    # 3. Seed Demo Data if DEMO_MODE=True
    if settings.DEMO_MODE:
        logger.info("DEMO_MODE is enabled; ensuring seed dataset exists...")
        try:
            await seed_database()
        except Exception as e:
            logger.error(f"Error while ensuring demo data: {e}", exc_info=True)

    # 4. Start Background Workers
    await sync_worker.start()
    await start_websocket_worker()

    logger.info(f"ScoutLab Backend successfully started in {settings.ENVIRONMENT} mode.")
    yield

    # Shutdown
    logger.info("Shutting down ScoutLab Backend...")
    await sync_worker.stop()
    await stop_websocket_worker()
    await cache.close()
    logger.info("ScoutLab Backend shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production Sorare Football Intelligence & Scouting Platform API for Lovable Frontend.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_and_log(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
    
    # Exclude high-frequency health checks from verbose logging
    if request.url.path != "/health":
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)"
        )
    return response


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "type": exc.__class__.__name__,
        },
    )


# Register Routers
app.include_router(health_router)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
        "api_v1": settings.API_V1_STR,
    }
