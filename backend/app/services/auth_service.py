from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)
from app.utils.security import hash_password, verify_password, create_access_token


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)

    async def register(self, req: UserRegisterRequest) -> UserResponse:
        existing_email = await self.repo.get_by_email(req.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists.",
            )
        existing_user = await self.repo.get_by_username(req.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken.",
            )

        hashed = hash_password(req.password)
        user = await self.repo.create_user(
            username=req.username,
            email=req.email,
            password_hash=hashed,
            group_name=req.group_name,
        )
        return UserResponse.model_validate(user)

    async def authenticate(self, req: UserLoginRequest) -> TokenResponse:
        user = await self.repo.get_by_username_or_email(req.email_or_username)
        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account."
            )

        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return TokenResponse(
            access_token=access_token,
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    async def get_user_profile(self, user_id: int) -> Optional[UserResponse]:
        user = await self.repo.get_by_id(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)
