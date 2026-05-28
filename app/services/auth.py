import math
import secrets
import string
from datetime import UTC, datetime, timedelta

from fastapi.exceptions import HTTPException
from pydantic import EmailStr
from starlette import status
from tortoise.transactions import in_transaction

from app.core.jwt.tokens import AccessToken, RefreshToken
from app.core.utils.common import normalize_phone_number
from app.core.utils.security import hash_password, verify_password
from app.dtos.auth import LoginRequest, SignUpRequest
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.services.jwt import JwtService

# REQ-AUTH-007 비밀번호 오류 잠금
MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 30


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.jwt_service = JwtService()

    async def signup(self, data: SignUpRequest) -> User:
        # 이메일 중복 체크
        await self.check_email_exists(data.email)

        # 입력받은 휴대폰 번호를 노말라이즈
        normalized_phone_number = normalize_phone_number(data.phone_number)

        # 휴대폰 번호 중복 체크
        await self.check_phone_number_exists(normalized_phone_number)

        # 유저 생성
        async with in_transaction():
            user = await self.user_repo.create_user(
                email=data.email,
                hashed_password=hash_password(data.password),  # 해시화된 비밀번호를 사용
                name=data.name,
                phone_number=normalized_phone_number,
                gender=data.gender,
                birthday=data.birth_date,
            )

            return user

    async def authenticate(self, data: LoginRequest) -> User:
        # 이메일로 사용자 조회
        email = str(data.email)
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="이메일 또는 비밀번호가 올바르지 않습니다."
            )

        # 비활성 계정 (탈퇴 등) 우선 차단
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="비활성화된 계정입니다.")

        # REQ-AUTH-007: 잠금 상태 체크
        now = datetime.now(UTC)
        if user.locked_until and user.locked_until > now:
            remaining_seconds = (user.locked_until - now).total_seconds()
            remaining_minutes = math.ceil(remaining_seconds / 60)
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"비밀번호 {MAX_FAILED_ATTEMPTS}회 이상 틀려 계정이 잠겼습니다. {remaining_minutes}분 후 다시 시도해주세요.",
            )

        # 비밀번호 검증
        if not verify_password(data.password, user.hashed_password):
            # 실패 카운터 +1
            user.failed_login_count += 1
            if user.failed_login_count >= MAX_FAILED_ATTEMPTS:
                # 5회 도달 — 30분 잠금 후 카운터 리셋
                user.locked_until = now + timedelta(minutes=LOCK_DURATION_MINUTES)
                user.failed_login_count = 0
                await user.save(update_fields=["failed_login_count", "locked_until", "updated_at"])
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"비밀번호를 {MAX_FAILED_ATTEMPTS}회 틀렸습니다. {LOCK_DURATION_MINUTES}분 후 다시 시도해주세요.",
                )
            await user.save(update_fields=["failed_login_count", "updated_at"])
            remaining_attempts = MAX_FAILED_ATTEMPTS - user.failed_login_count
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이메일 또는 비밀번호가 올바르지 않습니다. ({remaining_attempts}회 남음)",
            )

        # 비밀번호 성공 — 카운터·잠금 리셋
        if user.failed_login_count > 0 or user.locked_until is not None:
            user.failed_login_count = 0
            user.locked_until = None
            await user.save(update_fields=["failed_login_count", "locked_until", "updated_at"])

        return user

    async def login(self, user: User) -> dict[str, AccessToken | RefreshToken]:
        await self.user_repo.update_last_login(user.id)
        return self.jwt_service.issue_jwt_pair(user)

    async def check_email_exists(self, email: str | EmailStr) -> None:
        if await self.user_repo.exists_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용중인 이메일입니다.")

    async def check_phone_number_exists(self, phone_number: str) -> None:
        if await self.user_repo.exists_by_phone_number(phone_number):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용중인 휴대폰 번호입니다.")

    async def issue_temp_password(self, email: str) -> str:
        user = await self.user_repo.get_user_by_email(email)
        if not user or not user.is_active:
            # 계정 존재 여부를 노출하지 않기 위해 동일한 응답
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="등록된 이메일이 없습니다.")
        if user.hashed_password.startswith("SOCIAL:"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="소셜 로그인 계정은 임시 비밀번호를 사용할 수 없습니다."
            )
        alphabet = string.ascii_letters + string.digits + "!@#$"
        temp_pw = "".join(secrets.choice(alphabet) for _ in range(12))
        await self.user_repo.update_instance(user=user, data={"hashed_password": hash_password(temp_pw)})
        return temp_pw
