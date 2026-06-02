"""전역 에러 한국어 핸들러.

목적: 백엔드에서 발생하는 모든 에러 응답을 한국어로 통일.
한 번 등록하면 새 엔드포인트·DTO 추가 시 별도 작업 없이 자동 적용됨.

처리 범위:
- Pydantic 422 검증 에러 (이메일·길이·범위 등 표준 메시지 매핑)
- HTTPException (개발자가 한국어로 작성한 detail은 그대로 노출)
- 예상치 못한 500 예외 ("일시적 오류" 일반 메시지)

응답 형식 통일:
  {"detail": "<한국어 메시지>"}
  또는 검증 에러는 {"detail": [{"field": "email", "message": "..."}]}
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import ORJSONResponse

logger = logging.getLogger(__name__)


# Pydantic 검증 에러 type → 한국어 메시지 매핑
# 참고: https://docs.pydantic.dev/latest/errors/validation_errors/
_VALIDATION_MESSAGES: dict[str, str] = {
    "missing": "필수 입력 항목입니다.",
    "string_type": "문자열만 입력 가능합니다.",
    "int_type": "숫자(정수)만 입력 가능합니다.",
    "float_type": "숫자만 입력 가능합니다.",
    "bool_type": "참/거짓 값만 입력 가능합니다.",
    "string_too_short": "입력값이 너무 짧습니다.",
    "string_too_long": "입력값이 너무 깁니다.",
    "string_pattern_mismatch": "올바른 형식이 아닙니다.",
    "value_error": "올바르지 않은 값입니다.",
    "greater_than": "허용 범위를 벗어났습니다 (값이 너무 작습니다).",
    "greater_than_equal": "허용 범위를 벗어났습니다 (값이 너무 작습니다).",
    "less_than": "허용 범위를 벗어났습니다 (값이 너무 큽니다).",
    "less_than_equal": "허용 범위를 벗어났습니다 (값이 너무 큽니다).",
    "enum": "허용된 값 중에서 선택해주세요.",
    "date_parsing": "올바른 날짜 형식이 아닙니다 (YYYY-MM-DD).",
    "datetime_parsing": "올바른 날짜·시간 형식이 아닙니다.",
    "json_invalid": "올바른 JSON 형식이 아닙니다.",
    "model_type": "잘못된 요청 형식입니다.",
    "extra_forbidden": "허용되지 않은 항목이 포함됐습니다.",
}

# 특정 필드명에 대한 한국어 라벨
_FIELD_LABELS: dict[str, str] = {
    "email": "이메일",
    "password": "비밀번호",
    "name": "이름",
    "phone_number": "휴대폰 번호",
    "birth_date": "생년월일",
    "birthday": "생년월일",
    "gender": "성별",
    "current_password": "현재 비밀번호",
    "new_password": "새 비밀번호",
    "challenge_id": "챌린지",
    "user_challenge_id": "참여 챌린지",
    "item_code": "아이템",
    "amount": "금액",
}


def _korean_validation_message(error_type: str, ctx: dict, msg: str) -> str:
    """Pydantic 에러 type 코드 → 한국어 메시지."""
    msg_lower = (msg or "").lower()
    # 이메일·UUID 등 메시지 기반 우선 매핑 (type=value_error라도 잡힘)
    if "valid email" in msg_lower or "email" in (error_type or "").lower():
        return "올바른 이메일 형식이 아닙니다."
    if "uuid" in (error_type or "").lower() or "valid uuid" in msg_lower:
        return "올바른 ID 형식이 아닙니다."
    # 표준 type 매핑
    if error_type in _VALIDATION_MESSAGES:
        base = _VALIDATION_MESSAGES[error_type]
        if error_type == "string_too_short" and ctx and "min_length" in ctx:
            return f"최소 {ctx['min_length']}자 이상 입력해주세요."
        if error_type == "string_too_long" and ctx and "max_length" in ctx:
            return f"최대 {ctx['max_length']}자까지 입력 가능합니다."
        return base
    # fallback
    return msg or "올바르지 않은 입력입니다."


def _field_label(loc: tuple) -> str:
    """필드 위치 튜플에서 한국어 라벨 추출. (body, email) → '이메일'."""
    if not loc:
        return ""
    # body·query·path 키워드 제외, 실제 필드명만
    parts = [p for p in loc if p not in ("body", "query", "path", "header")]
    if not parts:
        return ""
    field_name = str(parts[-1])
    return _FIELD_LABELS.get(field_name, field_name)


def register_error_handlers(app: FastAPI) -> None:
    """FastAPI 앱에 글로벌 에러 핸들러 등록."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> ORJSONResponse:
        """Pydantic 422 → 한국어 메시지 변환.

        응답 예:
        {
          "detail": [
            {"field": "이메일", "message": "올바른 이메일 형식이 아닙니다."},
            {"field": "비밀번호", "message": "최소 8자 이상 입력해주세요."}
          ]
        }
        """
        items = []
        for err in exc.errors():
            field = _field_label(err.get("loc", ()))
            message = _korean_validation_message(
                error_type=err.get("type", ""),
                ctx=err.get("ctx", {}),
                msg=err.get("msg", ""),
            )
            items.append({"field": field, "message": message})
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": items},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> ORJSONResponse:
        """HTTPException은 detail 그대로 노출 (개발자가 한국어로 작성한 메시지)."""
        return ORJSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
        """예상치 못한 모든 예외 → 한국어 일반 메시지 + 로그."""
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "일시적 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
        )
