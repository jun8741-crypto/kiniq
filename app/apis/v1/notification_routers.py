from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import ORJSONResponse as Response

from app.dependencies.security import get_request_user
from app.dtos.notification import (
    NotificationListResponse,
    NotificationResponse,
    NotificationSettingResponse,
    NotificationSettingUpdateRequest,
)
from app.models.users import User
from app.services.notification import NotificationService

notification_router = APIRouter(prefix="/notifications", tags=["notifications"])


@notification_router.get(
    "",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="내 알림 목록",
)
async def list_notifications(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[NotificationService, Depends(NotificationService)],
    unread_only: Annotated[bool, Query(description="읽지 않은 알림만 조회")] = False,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Response:
    result = await service.get_notifications(
        user_id=user.id, unread_only=unread_only, limit=limit, offset=offset
    )
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@notification_router.patch(
    "/read-all",
    status_code=status.HTTP_200_OK,
    summary="전체 알림 읽음 처리",
)
async def mark_all_read(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[NotificationService, Depends(NotificationService)],
) -> Response:
    result = await service.mark_all_read(user_id=user.id)
    return Response(result, status_code=status.HTTP_200_OK)


@notification_router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="알림 읽음 처리",
)
async def mark_read(
    notification_id: int,
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[NotificationService, Depends(NotificationService)],
) -> Response:
    result = await service.mark_read(notification_id=notification_id, user_id=user.id)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@notification_router.get(
    "/settings",
    response_model=NotificationSettingResponse,
    status_code=status.HTTP_200_OK,
    summary="알림 설정 조회",
)
async def get_notification_settings(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[NotificationService, Depends(NotificationService)],
) -> Response:
    result = await service.get_settings(user_id=user.id)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@notification_router.patch(
    "/settings",
    response_model=NotificationSettingResponse,
    status_code=status.HTTP_200_OK,
    summary="알림 설정 변경",
)
async def update_notification_settings(
    request: NotificationSettingUpdateRequest,
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[NotificationService, Depends(NotificationService)],
) -> Response:
    result = await service.update_settings(user_id=user.id, data=request)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)
