from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.schemas.auth import MessageResponse
from app.admin_comp import AdminComponent
from app.api_router.deps import get_admin_component, RoleChecker

router = APIRouter(prefix="/admin", tags=["Administration"])

@router.post(
    "/users/{user_id}/lock", 
    response_model=MessageResponse, 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker(["Admin"]))]
)
async def lock_user(user_id: UUID, component: AdminComponent = Depends(get_admin_component)):
    return await component.lock_user_account(user_id)
