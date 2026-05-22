from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.schemas.profiles import ProfileUpdate, ProfileResponse
from app.services.auth_service import UserBusinessService
from app.api.deps import get_user_service, get_current_user_claims

router = APIRouter(prefix="/profiles", tags=["Profile Management"])

@router.put("/me", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def update_my_profile(
    profile_data: ProfileUpdate, 
    claims: dict = Depends(get_current_user_claims),
    service: UserBusinessService = Depends(get_user_service)
):
    user_id = UUID(claims.get("sub"))
    return await service.update_user_profile(user_id, profile_data)