"""Основной файл микросервиса Auth"""
import uuid
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import FastAPI, HTTPException, status
from passlib.context import CryptContext

from schemas import (
    UserRegister, UserResponse, UserLogin, TokenResponse,
    TokenRefresh, AccessTokenResponse, PasswordResetRequest,
    PasswordResetConfirm, MessageResponse
)
from models import DB, User, RefreshToken, PasswordReset, create_tables

app = FastAPI(title="Auth Service API")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "super_secret_jwt_key_for_auth_service"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


@app.middleware("http")
async def db_session_middleware(request, call_next):
    """Управление соединением с БД"""
    if DB.is_closed():
        DB.connect()
    try:
        response = await call_next(request)
    finally:
        if not DB.is_closed():
            DB.close()
    return response


@app.on_event("startup")
def startup():
    """Инициализация таблиц при запуске"""
    create_tables()


def create_access_token(data: dict):
    """Генерация JWT токена доступа"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/api/auth/register",
          response_model=UserResponse,
          status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister):
    """Регистрация нового пользователя"""
    if User.get_or_none(User.username == user_data.username):
        raise HTTPException(status_code=400, detail="Username taken")
    if User.get_or_none(User.email == user_data.email):
        raise HTTPException(status_code=400, detail="Email taken")

    hashed_password = pwd_context.hash(user_data.password)
    user = User.create(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    return UserResponse(id=user.id, username=user.username, email=user.email)


@app.post("/api/auth/login", response_model=TokenResponse)
def login(user_data: UserLogin):
    """Вход пользователя и выдача токенов"""
    user = User.get_or_none(User.username == user_data.username)
    if not user or not pwd_context.verify(user_data.password,
                                          user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username}
    )
    refresh_token_str = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    RefreshToken.create(user=user, token=refresh_token_str,
                        expires_at=expires_at)

    return TokenResponse(access_token=access_token,
                         refresh_token=refresh_token_str)


@app.post("/api/auth/refresh", response_model=AccessTokenResponse)
def refresh_token(token_data: TokenRefresh):
    """Обновление токена доступа"""
    token_record = RefreshToken.get_or_none(
        RefreshToken.token == token_data.refresh_token
    )
    if not token_record or token_record.expires_at < datetime.now():
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_access_token(
        data={"user_id": token_record.user.id,
              "username": token_record.user.username}
    )
    return AccessTokenResponse(access_token=access_token)


@app.post("/api/auth/reset-password/request", response_model=MessageResponse)
def request_password_reset(data: PasswordResetRequest):
    """Создание заявки на сброс пароля"""
    user = User.get_or_none(User.email == data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token_str = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(hours=1)

    PasswordReset.create(user=user, reset_token=reset_token_str,
                         expires_at=expires_at)
    return MessageResponse(message=f"Reset token: {reset_token_str}")


@app.post("/api/auth/reset-password/confirm", response_model=MessageResponse)
def confirm_password_reset(data: PasswordResetConfirm):
    """Установка нового пароля по токену"""
    reset_record = PasswordReset.get_or_none(
        (PasswordReset.reset_token == data.reset_token) &
        (PasswordReset.is_used is False)
    )

    if not reset_record or reset_record.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Invalid reset token")

    user = reset_record.user
    user.password_hash = pwd_context.hash(data.new_password)
    user.save()

    reset_record.is_used = True
    reset_record.save()

    return MessageResponse(message="Password successfully reset")
