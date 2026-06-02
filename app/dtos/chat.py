from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.dtos.base import BaseSerializerModel


class ChatMessageCreateRequest(BaseModel):
    question: Annotated[str, Field(min_length=1, max_length=2000, description="사용자 질문")]

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, v: str) -> str:
        """공백만 있는 질문 거부 (m-3)."""
        if not v.strip():
            raise ValueError("질문은 공백만으로 구성될 수 없습니다.")
        return v


class ChatMessageResponse(BaseSerializerModel):
    answer: str
    created_at: datetime
