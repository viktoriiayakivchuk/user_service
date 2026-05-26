from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User

class AdminComponent:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def lock_user_account(self, target_user_id: UUID) -> dict:
        result = await self.db.execute(
            select(User).filter(User.id == target_user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User account not found"
            )

        user.is_active = False
        self.db.add(user)
        await self.db.commit()
        return {"message": "User account successfully deactivated."}
