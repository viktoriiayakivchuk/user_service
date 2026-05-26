from fastapi import APIRouter, Depends, status
from app.schemas.auth import UserCreate, UserResponse, Token
from app.auth_comp import AuthenticationComponent
from app.api_router.deps import get_auth_component

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, component: AuthenticationComponent = Depends(get_auth_component)):
    return await component.register_new_user(user_data)

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(credentials: UserCreate, component: AuthenticationComponent = Depends(get_auth_component)):
    return await component.authenticate_user(credentials)
