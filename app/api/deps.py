from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.repository.user_repository import UserRepository
from app.services.auth_service import UserBusinessService

security = HTTPBearer()

async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserBusinessService:
    repo = UserRepository(db)
    return UserBusinessService(repo)

async def get_current_user_claims(auth_header: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        token = auth_header.credentials
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        return payload  
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials, missing or corrupt JWT token",
        )

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, claims: dict = Depends(get_current_user_claims)):
        user_role = claims.get("role")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted. Insufficient permissions (RBAC)."
            )
        return claims