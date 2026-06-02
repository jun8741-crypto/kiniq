import urllib.parse
from datetime import date
from typing import Annotated

import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse as Response
from fastapi.responses import RedirectResponse

from app.core import config
from app.core.config import Env
from app.core.rate_limit import limiter
from app.dtos.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    PasswordResetRequestBody,
    PasswordResetRequestResponse,
    PasswordResetVerifyBody,
    PasswordResetVerifyResponse,
    SignUpRequest,
    TokenRefreshResponse,
)
from app.repositories.user_repository import UserRepository
from app.services.auth import AuthService
from app.services.charge_mode import ChargeModeService
from app.services.jwt import JwtService
from app.services.points import PointService
from app.services.streak_protect import StreakProtectService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def signup(
    request: Request,
    body: SignUpRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Response:
    await auth_service.signup(body)
    return Response(content={"detail": "회원가입이 성공적으로 완료되었습니다."}, status_code=status.HTTP_201_CREATED)


@auth_router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
    point_service: Annotated[PointService, Depends(PointService)],
) -> Response:
    user = await auth_service.authenticate(body)
    tokens = await auth_service.login(user)
    today = date.today()
    # 일일 로그인 보상 (당일 첫 로그인 시 +10)
    await point_service.award_login(user.id, today)
    # 스트릭 보호권 자동 소모 평가 (어제 체크인 0회 + 보호권 보유 시)
    await StreakProtectService().evaluate(user.id, today)
    # 충전 모드 평가 (진입/경고 알림 트리거)
    await ChargeModeService().evaluate(user.id, today)
    resp = Response(
        content=LoginResponse(access_token=str(tokens["access_token"])).model_dump(), status_code=status.HTTP_200_OK
    )
    resp.set_cookie(
        key="refresh_token",
        value=str(tokens["refresh_token"]),
        httponly=True,
        secure=True if config.ENV == Env.PROD else False,
        samesite="lax",
        domain=config.COOKIE_DOMAIN or None,
        # 쿠키 만료를 refresh 토큰 수명과 일치 (이전: access exp(15분)를 잘못 사용 → SEC-2). max_age는 초 단위
        max_age=config.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )
    return resp


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> Response:
    resp = Response(content=None, status_code=status.HTTP_204_NO_CONTENT)
    resp.delete_cookie(key="refresh_token")
    return resp


def _oauth_error_redirect(msg: str) -> RedirectResponse:
    return RedirectResponse(f"{config.FRONTEND_URL}/?error={urllib.parse.quote(msg)}")


# ────────────────────────────────────────────────
# Kakao OAuth
# ────────────────────────────────────────────────


@auth_router.get("/kakao/login", summary="카카오 로그인 시작", tags=["social-auth"])
async def kakao_login() -> RedirectResponse:
    if not config.KAKAO_REST_API_KEY:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="카카오 앱 키가 설정되지 않았습니다.")
    params = urllib.parse.urlencode(
        {
            "client_id": config.KAKAO_REST_API_KEY,
            "redirect_uri": config.KAKAO_REDIRECT_URI,
            "response_type": "code",
            "scope": "account_email,profile_nickname",
        }
    )
    return RedirectResponse(f"https://kauth.kakao.com/oauth/authorize?{params}")


@auth_router.get("/kakao/callback", summary="카카오 OAuth 콜백", tags=["social-auth"])
async def kakao_callback(code: str | None = None, error: str | None = None) -> RedirectResponse:
    if error or not code:
        return _oauth_error_redirect("카카오 로그인이 취소되었습니다.")

    async with httpx.AsyncClient() as client:
        # 1. 인가 코드 → 액세스 토큰
        token_resp = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": config.KAKAO_REST_API_KEY,
                "redirect_uri": config.KAKAO_REDIRECT_URI,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_resp.status_code != 200:
            return _oauth_error_redirect("카카오 토큰 발급에 실패했습니다.")
        kakao_access_token = token_resp.json().get("access_token", "")

        # 2. 액세스 토큰 → 사용자 정보
        me_resp = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {kakao_access_token}"},
        )
        if me_resp.status_code != 200:
            return _oauth_error_redirect("카카오 사용자 정보 조회에 실패했습니다.")
        me = me_resp.json()

    provider_id = str(me.get("id", ""))
    kakao_account = me.get("kakao_account", {})
    email = kakao_account.get("email", f"kakao_{provider_id}@kakao.social")
    name = me.get("properties", {}).get("nickname") or kakao_account.get("profile", {}).get("nickname", "카카오사용자")

    user_repo = UserRepository()
    jwt_service = JwtService()
    user, _ = await user_repo.get_or_create_social_user(
        email=email, name=name, provider="kakao", provider_id=provider_id
    )
    await user_repo.update_last_login(user.id)
    today = date.today()
    await PointService().award_login(user.id, today)
    await StreakProtectService().evaluate(user.id, today)
    await ChargeModeService().evaluate(user.id, today)
    access_token = jwt_service.create_access_token(user)

    return RedirectResponse(f"{config.FRONTEND_URL}/oauth/callback?token={access_token}")


# ────────────────────────────────────────────────
# Google OAuth
# ────────────────────────────────────────────────


@auth_router.get("/google/login", summary="구글 로그인 시작", tags=["social-auth"])
async def google_login() -> RedirectResponse:
    if not config.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Google 클라이언트 ID가 설정되지 않았습니다."
        )
    params = urllib.parse.urlencode(
        {
            "client_id": config.GOOGLE_CLIENT_ID,
            "redirect_uri": config.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "online",
        }
    )
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")


@auth_router.get("/google/callback", summary="구글 OAuth 콜백", tags=["social-auth"])
async def google_callback(code: str | None = None, error: str | None = None) -> RedirectResponse:
    if error or not code:
        return _oauth_error_redirect("구글 로그인이 취소되었습니다.")

    async with httpx.AsyncClient() as client:
        # 1. 인가 코드 → 액세스 토큰
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "grant_type": "authorization_code",
                "client_id": config.GOOGLE_CLIENT_ID,
                "client_secret": config.GOOGLE_CLIENT_SECRET,
                "redirect_uri": config.GOOGLE_REDIRECT_URI,
                "code": code,
            },
        )
        if token_resp.status_code != 200:
            return _oauth_error_redirect("구글 토큰 발급에 실패했습니다.")
        google_access_token = token_resp.json().get("access_token", "")

        # 2. 액세스 토큰 → 사용자 정보
        me_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {google_access_token}"},
        )
        if me_resp.status_code != 200:
            return _oauth_error_redirect("구글 사용자 정보 조회에 실패했습니다.")
        me = me_resp.json()

    provider_id = me.get("id", "")
    email = me.get("email", f"google_{provider_id}@google.social")
    name = me.get("name") or me.get("given_name", "구글사용자")

    user_repo = UserRepository()
    jwt_service = JwtService()
    user, _ = await user_repo.get_or_create_social_user(
        email=email, name=name, provider="google", provider_id=provider_id
    )
    await user_repo.update_last_login(user.id)
    today = date.today()
    await PointService().award_login(user.id, today)
    await StreakProtectService().evaluate(user.id, today)
    await ChargeModeService().evaluate(user.id, today)
    access_token = jwt_service.create_access_token(user)

    return RedirectResponse(f"{config.FRONTEND_URL}/oauth/callback?token={access_token}")


@auth_router.get("/token/refresh", response_model=TokenRefreshResponse, status_code=status.HTTP_200_OK)
async def token_refresh(
    jwt_service: Annotated[JwtService, Depends(JwtService)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing.")
    access_token = jwt_service.refresh_jwt(refresh_token)
    return Response(
        content=TokenRefreshResponse(access_token=str(access_token)).model_dump(), status_code=status.HTTP_200_OK
    )


@auth_router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="임시 비밀번호 발급 (즉시·구버전)",
    description="이메일로 임시 비밀번호를 즉시 발급합니다. 발급 즉시 기존 비밀번호는 무효화됩니다.",
    deprecated=True,
)
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Response:
    temp_pw = await auth_service.issue_temp_password(email=str(body.email))
    return Response(content=ForgotPasswordResponse(temp_password=temp_pw).model_dump(), status_code=status.HTTP_200_OK)


@auth_router.post(
    "/password-reset/request",
    response_model=PasswordResetRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="비밀번호 재설정 코드 요청",
    description=(
        "이메일로 6자리 인증 코드를 발송합니다 (TTL 5분). EMAIL_MODE=demo일 경우 응답에 코드를 직접 반환합니다(시연용)."
    ),
)
@limiter.limit("5/minute")
async def request_password_reset(
    request: Request,
    body: PasswordResetRequestBody,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Response:
    result = await auth_service.request_password_reset(email=str(body.email))
    return Response(
        content=PasswordResetRequestResponse(
            sent=result.sent,
            mode=result.mode,
            demo_code=result.demo_code,
            expires_in_seconds=config.PASSWORD_RESET_CODE_TTL_SECONDS,
        ).model_dump(),
        status_code=status.HTTP_200_OK,
    )


@auth_router.post(
    "/password-reset/verify",
    response_model=PasswordResetVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="비밀번호 재설정 코드 검증 + 임시 비밀번호 발급",
    description="6자리 코드 검증 후 임시 비밀번호를 발급합니다. 검증 실패 5회 초과 시 코드 무효화.",
)
@limiter.limit("10/minute")
async def verify_password_reset(
    request: Request,
    body: PasswordResetVerifyBody,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Response:
    temp_pw = await auth_service.verify_password_reset(email=str(body.email), code=body.code)
    return Response(
        content=PasswordResetVerifyResponse(temp_password=temp_pw).model_dump(),
        status_code=status.HTTP_200_OK,
    )
