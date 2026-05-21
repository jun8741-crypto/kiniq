from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import ORJSONResponse as Response

from app.dependencies.security import get_request_user
from app.dtos.diet_survey import DietSurveyCreateRequest, DietSurveyListResponse, DietSurveyResponse, SurveyStatusResponse
from app.models.users import User
from app.services.diet_survey import DietSurveyService

diet_survey_router = APIRouter(prefix="/diet-surveys", tags=["diet-surveys"])
surveys_router = APIRouter(prefix="/surveys", tags=["surveys"])


@diet_survey_router.post(
    "",
    response_model=DietSurveyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="식이 설문 등록",
)
async def create_diet_survey(
    request: DietSurveyCreateRequest,
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[DietSurveyService, Depends(DietSurveyService)],
) -> Response:
    result = await service.create_survey(user_id=user.id, dto=request)
    return Response(result.model_dump(), status_code=status.HTTP_201_CREATED)


@diet_survey_router.get(
    "",
    response_model=DietSurveyListResponse,
    status_code=status.HTTP_200_OK,
    summary="식이 설문 이력 목록",
)
async def list_diet_surveys(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[DietSurveyService, Depends(DietSurveyService)],
) -> Response:
    result = await service.get_surveys(user_id=user.id)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@surveys_router.get(
    "/status",
    response_model=SurveyStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="설문 완료 여부 조회",
)
async def get_survey_status(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[DietSurveyService, Depends(DietSurveyService)],
) -> Response:
    result = await service.get_survey_status(user_id=user.id)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)
