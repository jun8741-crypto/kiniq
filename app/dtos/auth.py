from datetime import date
from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr, Field

from app.core.validators import validate_birthday, validate_password, validate_phone_number
from app.models.users import Gender


class SignUpRequest(BaseModel):
    email: Annotated[
        EmailStr,
        Field(None, max_length=40),
    ]
    password: Annotated[str, Field(min_length=8), AfterValidator(validate_password)]
    name: Annotated[str, Field(max_length=20)]
    gender: Gender
    birth_date: Annotated[date, AfterValidator(validate_birthday)]
    phone_number: Annotated[str, AfterValidator(validate_phone_number)]


class LoginRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]


class LoginResponse(BaseModel):
    access_token: str


class TokenRefreshResponse(LoginResponse): ...


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    temp_password: str


class PasswordResetRequestBody(BaseModel):
    email: EmailStr


class PasswordResetRequestResponse(BaseModel):
    sent: bool
    mode: str
    demo_code: str | None = None
    expires_in_seconds: int


class PasswordResetVerifyBody(BaseModel):
    email: EmailStr
    code: Annotated[str, Field(min_length=6, max_length=6, pattern=r"^\d{6}$")]


class PasswordResetVerifyResponse(BaseModel):
    temp_password: str
