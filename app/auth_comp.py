from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.models.user import User
from app.models.role import Role
from app.models.profile import Profile
from app.schemas.auth import UserCreate, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.event_pub import event_publisher

class AuthenticationComponent:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User)
            .filter(User.email == email)
            .options(joinedload(User.role))
        )
        return result.scalars().first()

    async def get_role_by_name(self, role_name: str) -> Role | None:
        result = await self.db.execute(
            select(Role).filter(Role.name == role_name)
        )
        return result.scalars().first()

    async def register_new_user(self, user_data: UserCreate) -> User:
        existing_user = await self.get_by_email(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        role = await self.get_role_by_name("Student")
        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default system role 'Student' not initialized in database"
            )

        hashed_password = get_password_hash(user_data.password)

        new_user = User(
            email=user_data.username,
            hashed_password=hashed_password,
            role_id=role.id,
            is_active=True
        )
        self.db.add(new_user)
        await self.db.flush() 

        new_profile = Profile(
            user_id=new_user.id,
            first_name="New",
            last_name="User"
        )
        self.db.add(new_profile)
        await self.db.commit()

        # Publish domain event asynchronously via event publisher component
        event_publisher.publish_user_registered(
            user_id=str(new_user.id),
            email=new_user.email,
            role=role.name,
            created_at=new_user.created_at.isoformat() if new_user.created_at else None
        )

        return new_user

    async def authenticate_user(self, credentials: UserCreate) -> Token:
        user = await self.get_by_email(credentials.username)
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
