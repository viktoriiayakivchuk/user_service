from uuid import UUID
from fastapi import HTTPException, status
from app.repository.user_repository import UserRepository
from app.schemas.auth import UserCreate, Token
from app.schemas.profiles import ProfileUpdate
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.messaging import event_publisher

class UserBusinessService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_new_user(self, user_data: UserCreate):
        existing_user = await self.user_repo.get_by_email(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        role = await self.user_repo.get_role_by_name("Student")
        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default system role 'Student' not initialized in database"
            )

        hashed_password = get_password_hash(user_data.password)

        new_user_dict = {
            "email": user_data.username,
            "hashed_password": hashed_password,
            "role_id": role.id,
            "is_active": True
        }
        new_user = await self.user_repo.create(new_user_dict)
        await self.user_repo.db_session.flush() 

        profile_dict = {
            "user_id": new_user.id,
            "first_name": "New",
            "last_name": "User"
        }
        await self.user_repo.create_profile(profile_dict)

        await self.user_repo.db_session.commit()

        event_publisher.publish_user_registered(
            user_id=str(new_user.id),
            email=new_user.email,
            role=role.name,
            created_at=new_user.created_at.isoformat() if new_user.created_at else None
        )

        return new_user

    async def authenticate_user(self, credentials: UserCreate) -> Token:
        user = await self.user_repo.get_by_email(credentials.username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is locked out by administrator")

        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = create_access_token(subject=user.id, role=user.role.name)
        
        return Token(
            access_token=access_token,
            refresh_token="mock_stateless_refresh_token_uuid",
            token_type="bearer"
        )

    async def update_user_profile(self, user_id: UUID, profile_data: ProfileUpdate):
        profile = await self.user_repo.get_profile_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        update_dict = profile_data.model_dump(exclude_none=True)
        updated_profile = await self.user_repo.update(profile, update_dict)
        await self.user_repo.db_session.commit()
        return updated_profile

    async def lock_user_account(self, target_user_id: UUID):
        user = await self.user_repo.get(target_user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found")

        await self.user_repo.update(user, {"is_active": False})
        await self.user_repo.db_session.commit()
        return {"message": "User successfully locked"}