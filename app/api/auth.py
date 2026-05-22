from fastapi import APIRouter, Depends, status
from app.schemas.auth import UserCreate, UserResponse, Token
from app.services.auth_service import UserBusinessService
from app.api.deps import get_user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, service: UserBusinessService = Depends(get_user_service)):
    return await service.register_new_user(user_data)

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(credentials: UserCreate, service: UserBusinessService = Depends(get_user_service)):
    return await service.authenticate_user(credentials)