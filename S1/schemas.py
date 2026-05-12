"""Схемы валидации данных для сервиса Auth"""
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Схема регистрации нового пользователя"""
    username: str = Field(..., min_length=1)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя"""
    id: int
    username: str
    email: str


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Схема ответа с access и refresh токенами"""
    access_token: str
    refresh_token: str


class TokenRefresh(BaseModel):
    """Схема для обновления access токена"""
    refresh_token: str


class AccessTokenResponse(BaseModel):
    """Схема ответа с новым access токеном"""
    access_token: str


class PasswordResetRequest(BaseModel):
    """Схема запроса на сброс пароля"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Схема подтверждения сброса пароля"""
    reset_token: str
    new_password: str = Field(..., min_length=8)


class MessageResponse(BaseModel):
    """Универсальная схема для текстовых сообщений"""
    message: str
