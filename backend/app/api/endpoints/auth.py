from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse, ApiMeta
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ApiResponse[UserResponse])
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new private syndicate user."""
    service = AuthService(db)
    user = await service.register(req)
    return ApiResponse(data=user, meta=ApiMeta(source="scoutlab"))


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and obtain JWT access token."""
    service = AuthService(db)
    token = await service.authenticate(req)
    return ApiResponse(data=token, meta=ApiMeta(source="scoutlab"))


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get authenticated user profile."""
    return ApiResponse(
        data=UserResponse.model_validate(current_user),
        meta=ApiMeta(source="scoutlab"),
    )
