from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.schemas.auth import MessageResponse
from app.services.auth_service import UserBusinessService
from app.api.deps import get_user_service, RoleChecker

router = APIRouter(prefix="/admin", tags=["Administration"])

@router.post(
    "/users/{user_id}/lock", 
    response_model=MessageResponse, 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker(["Admin"]))]
)
async def lock_user(user_id: UUID, service: UserBusinessService = Depends(get_user_service)):
    return await service.lock_user_account(user_id)