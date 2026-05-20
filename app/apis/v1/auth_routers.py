import urllib.parse
from typing import Annotated

import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException, status
from fastapi.responses import JSONResponse as Response
from fastapi.responses import RedirectResponse

from app.core import config
from app.core.config import Env
from app.dtos.auth import LoginRequest, LoginResponse, SignUpRequest, TokenRefreshResponse
from app.repositories.user_repository import UserRepository
from app.services.auth import AuthService
from app.services.jwt import JwtService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignUpRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Response:
    await auth_service.signup(request)
    return Response(content={"detail": "회원가입이 성공적으로 완료되었습니다."}, status_code=status.HTTP_201_CREATED)


@auth_router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Response:
    user = await auth_service.authenticate(request)
    tokens = await auth_service.login(user)
    resp = Response(
        content=LoginResponse(access_token=str(tokens["access_token"])).model_dump(), status_code=status.HTTP_200_OK
    )
    resp.set_cookie(
        key="refresh_token",
        value=str(tokens["refresh_token"]),
        httponly=True,
        secure=True if config.ENV == Env.PROD else False,
        domain=config.COOKIE_DOMAIN or None,
        expires=tokens["access_token"].payload["exp"],
    )
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
    params = urllib.parse.urlencode({
        "client_id": config.KAKAO_REST_API_KEY,
        "redirect_uri": config.KAKAO_REDIRECT_URI,
        "response_type": "code",
        "scope": "account_email,profile_nickname",
    })
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
    access_token = jwt_service.create_access_token(user)

    return RedirectResponse(
        f"{config.FRONTEND_URL}/oauth/callback?token={access_token}"
    )


# ────────────────────────────────────────────────
# Google OAuth
# ────────────────────────────────────────────────

@auth_router.get("/google/login", summary="구글 로그인 시작", tags=["social-auth"])
async def google_login() -> RedirectResponse:
    if not config.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Google 클라이언트 ID가 설정되지 않았습니다.")
    params = urllib.parse.urlencode({
        "client_id": config.GOOGLE_CLIENT_ID,
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
    })
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
    access_token = jwt_service.create_access_token(user)

    return RedirectResponse(
        f"{config.FRONTEND_URL}/oauth/callback?token={access_token}"
    )


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
