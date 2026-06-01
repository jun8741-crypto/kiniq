from fastapi import HTTPException
from starlette import status
from tortoise.transactions import in_transaction

from app.core.utils.common import normalize_phone_number
from app.core.utils.security import hash_password, verify_password
from app.dtos.users import PasswordChangeRequest, UserUpdateRequest
from app.models.challenge import CheckinEmotionLog
from app.models.diet_survey import DietSurvey
from app.models.health_check import HealthCheck
from app.models.lifestyle_survey import LifestyleSurvey
from app.models.password_reset import PasswordResetCode
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.services.auth import AuthService


class UserManageService:
    def __init__(self):
        self.repo = UserRepository()
        self.auth_service = AuthService()

    async def update_user(self, user: User, data: UserUpdateRequest) -> User:
        if data.email:
            await self.auth_service.check_email_exists(data.email)
        if data.phone_number:
            normalized_phone_number = normalize_phone_number(data.phone_number)
            await self.auth_service.check_phone_number_exists(normalized_phone_number)
            data.phone_number = normalized_phone_number
        async with in_transaction():
            await self.repo.update_instance(user=user, data=data.model_dump(exclude_none=True))
            await user.refresh_from_db()
        return user

    async def change_password(self, user: User, data: PasswordChangeRequest) -> None:
        if user.hashed_password.startswith("SOCIAL:"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="소셜 로그인 계정은 비밀번호를 변경할 수 없습니다.",
            )
        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="현재 비밀번호가 올바르지 않습니다.",
            )
        await self.repo.update_instance(user=user, data={"hashed_password": hash_password(data.new_password)})

    async def delete_account(self, user: User) -> None:
        """REQ-SEC-008: 회원 탈퇴 시 민감의료정보 즉시 파기.

        파기 대상 (즉시):
        - HealthCheck (검진 결과, 혈압·혈당·eGFR 등)
        - LifestyleSurvey (흡연·음주·운동 등 민감 생활습관)
        - DietSurvey (식단 민감 항목)
        - CheckinEmotionLog (감정 기록)
        - PasswordResetCode (인증 코드)

        보존 (14일 후 영구 삭제 — 익명화된 메타로):
        - UserChallenge, PointTransaction, Notification 등 (가명 ID로 식별 불가능)
        """
        async with in_transaction():
            # 민감의료 즉시 파기
            await HealthCheck.filter(user_id=user.id).delete()
            await LifestyleSurvey.filter(user_id=user.id).delete()
            await DietSurvey.filter(user_id=user.id).delete()
            await CheckinEmotionLog.filter(user_id=user.id).delete()
            await PasswordResetCode.filter(user_id=user.id).delete()
            # 식별정보 익명화 + 비활성화 (메타데이터는 14일 보존)
            await self.repo.anonymize_and_deactivate(user)
