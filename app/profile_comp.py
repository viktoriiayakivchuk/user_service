from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.profile import Profile
from app.schemas.profiles import ProfileUpdate

class ProfileComponent:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile_by_user_id(self, user_id: UUID) -> Profile | None:
        result = await self.db.execute(
            select(Profile).filter(Profile.user_id == user_id)
        )
        return result.scalars().first()

    async def update_user_profile(self, user_id: UUID, profile_data: ProfileUpdate) -> Profile:
        profile = await self.get_profile_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Profile not found"
            )

        update_data = profile_data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        self.db.add(profile)
        await self.db.commit()
        return profile
