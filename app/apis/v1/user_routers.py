from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import ORJSONResponse as Response

from app.dependencies.security import get_request_user
from app.dtos.users import PasswordChangeRequest, UserInfoResponse, UserUpdateRequest
from app.models.users import User
from app.services.users import UserManageService

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/me", response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
async def user_me_info(
    user: Annotated[User, Depends(get_request_user)],
) -> Response:
    return Response(UserInfoResponse.model_validate(user).model_dump(), status_code=status.HTTP_200_OK)


@user_router.patch("/me", response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
async def update_user_me_info(
    update_data: UserUpdateRequest,
    user: Annotated[User, Depends(get_request_user)],
    user_manage_service: Annotated[UserManageService, Depends(UserManageService)],
) -> Response:
    updated_user = await user_manage_service.update_user(user=user, data=update_data)
    return Response(UserInfoResponse.model_validate(updated_user).model_dump(), status_code=status.HTTP_200_OK)


@user_router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: PasswordChangeRequest,
    user: Annotated[User, Depends(get_request_user)],
    user_manage_service: Annotated[UserManageService, Depends(UserManageService)],
) -> None:
    await user_manage_service.change_password(user=user, data=data)


@user_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    user: Annotated[User, Depends(get_request_user)],
    user_manage_service: Annotated[UserManageService, Depends(UserManageService)],
) -> Response:
    await user_manage_service.delete_account(user=user)
    resp = Response(None, status_code=status.HTTP_204_NO_CONTENT)
    resp.delete_cookie(key="refresh_token")
    return resp
