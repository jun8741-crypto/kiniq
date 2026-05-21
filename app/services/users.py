from fastapi import HTTPException
from starlette import status
from tortoise.transactions import in_transaction

from app.core.utils.common import normalize_phone_number
from app.core.utils.security import hash_password, verify_password
from app.dtos.users import PasswordChangeRequest, UserUpdateRequest
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
        await self.repo.anonymize_and_deactivate(user)
