from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.repository.base import BaseRepository
from app.models.user import User
from app.models.role import Role
from app.models.profile import Profile

class UserRepository(BaseRepository[User]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db_session.execute(
            select(User)
            .filter(User.email == email)
            .options(joinedload(User.role))
        )
        return result.scalars().first()

    async def get_role_by_name(self, role_name: str) -> Role | None:
        result = await self.db_session.execute(
            select(Role).filter(Role.name == role_name)
        )
        return result.scalars().first()

    async def get_profile_by_user_id(self, user_id: UUID) -> Profile | None:
        result = await self.db_session.execute(
            select(Profile).filter(Profile.user_id == user_id)
        )
        return result.scalars().first()

    async def create_profile(self, profile_data: dict) -> Profile:
        db_profile = Profile(**profile_data)
        self.db_session.add(db_profile)
        return db_profile