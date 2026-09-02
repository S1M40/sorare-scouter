import os
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # General
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @field_validator("DEBUG", "DEMO_MODE", mode="before")
    @classmethod
    def parse_bool(cls, v) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            v_lower = v.lower()
            if v_lower in ("false", "0", "no", "f", "release"):
                return False
            return True
        return bool(v)
    PROJECT_NAME: str = "ScoutLab Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security & Auth
    SECRET_KEY: str = "scoutlab-super-secret-key-change-in-production-minimum-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080", "*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./scoutlab.db"
    POSTGRES_USER: str = "scoutlab"
    POSTGRES_PASSWORD: str = "scoutlab_secret"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "scoutlab"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info) -> str:
        if v and v.strip():
            # Ensure proper async driver prefix
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            if v.startswith("sqlite://") and not v.startswith("sqlite+aiosqlite://"):
                return v.replace("sqlite://", "sqlite+aiosqlite://", 1)
            return v
        # Fallback to sqlite for ease of standalone local development/tests
        return "sqlite+aiosqlite:///./scoutlab.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Demo Mode
    DEMO_MODE: bool = True

    # Sorare Integration
    SORARE_GRAPHQL_URL: str = "https://api.sorare.com/federation/graphql"
    SORARE_WS_URL: str = "wss://ws.sorare.com/cable"
    SORARE_API_KEY: str = ""
    SORARE_JWT: str = ""

    # Analytics Engine Weights (Deterministic weights)
    FORM_WEIGHT: float = 0.25
    CONSISTENCY_WEIGHT: float = 0.15
    MINUTES_WEIGHT: float = 0.15
    FIXTURE_WEIGHT: float = 0.15
    AVAILABILITY_WEIGHT: float = 0.15
    MARKET_WEIGHT: float = 0.15

    # Synchronization
    SYNC_INTERVAL_MINUTES: int = 30


settings = Settings()
