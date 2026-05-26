from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.schemas.profiles import ProfileUpdate, ProfileResponse
from app.profile_comp import ProfileComponent
from app.api_router.deps import get_profile_component, get_current_user_claims

router = APIRouter(prefix="/profiles", tags=["Profile Management"])

@router.put("/me", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def update_my_profile(
    profile_data: ProfileUpdate, 
    claims: dict = Depends(get_current_user_claims),
    component: ProfileComponent = Depends(get_profile_component)
):
    user_id = UUID(claims.get("sub"))
    return await component.update_user_profile(user_id, profile_data)
