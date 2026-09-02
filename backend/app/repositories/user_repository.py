from typing import Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email.lower().strip())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(User).where(User.username == username.strip())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        clean = identifier.strip().lower()
        query = select(User).where(
            or_(User.username.ilike(clean), User.email == clean)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create_user(
        self, username: str, email: str, password_hash: str, group_name: Optional[str] = None
    ) -> User:
        user = User(
            username=username.strip(),
            email=email.strip().lower(),
            password_hash=password_hash,
            group_name=group_name or "ScoutLab Alpha Syndicate",
        )
        self.session.add(user)
        await self.session.flush()
        return user
