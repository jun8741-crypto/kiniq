from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import ORJSONResponse as Response

from app.dependencies.security import get_request_user
from app.dtos.lifestyle_survey import (
    LifestyleSurveyCreateRequest,
    LifestyleSurveyListResponse,
    LifestyleSurveyResponse,
)
from app.models.users import User
from app.services.lifestyle_survey import LifestyleSurveyService

lifestyle_survey_router = APIRouter(prefix="/lifestyle-surveys", tags=["lifestyle-surveys"])


@lifestyle_survey_router.post(
    "",
    response_model=LifestyleSurveyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="생활습관 설문 등록",
)
async def create_survey(
    request: LifestyleSurveyCreateRequest,
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[LifestyleSurveyService, Depends(LifestyleSurveyService)],
) -> Response:
    result = await service.create_survey(user_id=user.id, dto=request)
    return Response(result.model_dump(), status_code=status.HTTP_201_CREATED)


@lifestyle_survey_router.get(
    "",
    response_model=LifestyleSurveyListResponse,
    status_code=status.HTTP_200_OK,
    summary="생활습관 설문 이력 목록",
)
async def list_surveys(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[LifestyleSurveyService, Depends(LifestyleSurveyService)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Response:
    result = await service.get_surveys(user_id=user.id, limit=limit, offset=offset)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@lifestyle_survey_router.get(
    "/{survey_id}",
    response_model=LifestyleSurveyResponse,
    status_code=status.HTTP_200_OK,
    summary="생활습관 설문 단건 조회",
)
async def get_survey(
    survey_id: int,
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[LifestyleSurveyService, Depends(LifestyleSurveyService)],
) -> Response:
    result = await service.get_survey(survey_id=survey_id, user_id=user.id)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)
