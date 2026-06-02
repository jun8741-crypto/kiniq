import pytest
from pydantic import ValidationError
from app.dtos.chat import ChatMessageCreateRequest


def test_request_accepts_question():
    req = ChatMessageCreateRequest(question="단백질 권장량은?")
    assert req.question == "단백질 권장량은?"


def test_request_rejects_empty():
    with pytest.raises(ValidationError):
        ChatMessageCreateRequest(question="")


def test_request_rejects_whitespace_only():
    """공백만 있는 질문도 ValidationError — m-3 공백 가드 확인."""
    with pytest.raises(ValidationError):
        ChatMessageCreateRequest(question="   ")
