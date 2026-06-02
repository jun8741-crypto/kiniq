from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.dtos.base import BaseSerializerModel


class ChatMessageCreateRequest(BaseModel):
    question: Annotated[str, Field(min_length=1, max_length=2000, description="사용자 질문")]


class ChatMessageResponse(BaseSerializerModel):
    answer: str
    created_at: datetime
