from datetime import datetime, timezone
from enum import Enum
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PositionEnum(str, Enum):
    GOALKEEPER = "Goalkeeper"
    DEFENDER = "Defender"
    MIDFIELDER = "Midfielder"
    FORWARD = "Forward"


class RarityEnum(str, Enum):
    LIMITED = "limited"
    RARE = "rare"
    SUPER_RARE = "super_rare"
    UNIQUE = "unique"
    CUSTOM = "custom"


class RecommendationEnum(str, Enum):
    BUY = "BUY"
    WATCH = "WATCH"
    HOLD = "HOLD"
    SELL = "SELL"
    AVOID = "AVOID"


class RiskLevelEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SourceTypeEnum(str, Enum):
    FACT = "FACT"
    REPORT = "REPORT"
    PREDICTION = "PREDICTION"


class SeverityEnum(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    SUCCESS = "SUCCESS"


class ApiMeta(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "scoutlab"
    data_updated_at: Optional[str] = None
    stale: bool = False


class ApiPaginationMeta(ApiMeta):
    page: int = 1
    page_size: int = 25
    total: int = 0
    total_pages: int = 1


class ApiResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    data: T
    meta: ApiMeta = Field(default_factory=ApiMeta)


class ApiListResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    data: List[T]
    meta: ApiPaginationMeta
