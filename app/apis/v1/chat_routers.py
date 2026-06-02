from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import ORJSONResponse as Response

from app.dependencies.security import get_request_user
from app.dtos.chat import ChatMessageCreateRequest, ChatMessageResponse
from app.models.users import User
from app.services.chat import ChatService

chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post(
    "/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="RAG 챗봇에 질문",
)
async def create_message(
    request: ChatMessageCreateRequest,
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[ChatService, Depends(ChatService)],
) -> Response:
    result = await service.ask(user_id=user.id, question=request.question)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)
