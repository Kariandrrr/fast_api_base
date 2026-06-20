import json
import logging
import re
import uuid
from typing import Optional, TYPE_CHECKING

from fastapi_users import BaseUserManager, UUIDIDMixin, InvalidPasswordException
from fastapi_users.db import SQLAlchemyUserDatabase
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.models import User
from .refresh_token import RefreshTokenService

if TYPE_CHECKING:
    from fastapi import Request, Response

log = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    # Сброс пароля
    reset_password_token_secret: str = settings.auth.jwt.reset_password_token_secret
    reset_password_token_lifetime_seconds: int = (
        settings.auth.jwt.reset_password_token_lifetime_seconds
    )
    reset_password_token_audience: str = settings.auth.jwt.reset_password_token_audience
    # Подтверждение email
    verification_token_secret: str = settings.auth.jwt.verification_token_secret
    verification_token_lifetime_seconds: int = (
        settings.auth.jwt.verification_token_lifetime_seconds
    )
    verification_token_audience: str = settings.auth.jwt.verification_token_audience

    def __init__(
        self,
        user_db: SQLAlchemyUserDatabase,
        refresh_token_service: RefreshTokenService,
    ):
        super().__init__(user_db)
        self._refresh_token_service = refresh_token_service

    async def validate_password(self, password: str, user=None) -> None:  # noqa: ARG002
        errors = []
        if len(password) < 8:
            errors.append("минимум 8 символов")
        if not re.search(r"[A-ZА-ЯЁ]", password):
            errors.append("заглавная буква")
        if not re.search(r"[a-zа-яё]", password):
            errors.append("строчная буква")
        if not re.search(r"[0-9]", password):
            errors.append("цифра")
        if not re.search(r"[^A-Za-zА-ЯЁа-яё0-9\s]", password):
            errors.append("спецсимвол (не пробел)")
        if re.search(r"\s", password):
            errors.append("пробелы запрещены")
        if errors:
            raise InvalidPasswordException(
                reason=f"Пароль должен содержать: {', '.join(errors)}"
            )

    async def on_after_login(
        self,
        user: User,
        request: Optional["Request"] = None,
        response: Optional["Response"] = None,
    ):
        refresh_token = await self._refresh_token_service.write_token(user)

        await self._refresh_token_service.redis.set(
            f"user_version:{user.id}",
            user.token_version,
        )

        if response is None:
            log.warning("on_after_login: response is None, refresh token не выдан")
            return

        if isinstance(response, JSONResponse):
            # Bearer транспорт — добавляем refresh_token в тело ответа
            body = json.loads(response.body)
            body["refresh_token"] = refresh_token
            new_body = json.dumps(body).encode("utf-8")
            response.body = new_body
            response.headers["content-length"] = str(len(new_body))
        else:
            # Cookie транспорт — ставим отдельную httpOnly cookie
            response.set_cookie(
                key=settings.auth.cookie.refresh_name,
                value=refresh_token,
                max_age=settings.auth.jwt.refresh_token_lifetime_seconds,
                path=settings.auth.cookie.refresh_path,
                domain=settings.auth.cookie.domain,
                secure=settings.auth.cookie.secure,
                httponly=settings.auth.cookie.httponly,
                samesite=settings.auth.cookie.samesite,
            )

        log.info("on_after_login: выдан refresh токен user_id=%s", user.id)

    async def increment_token_version(self, user: User) -> User:
        user = await self.user_db.update(
            user, {"token_version": user.token_version + 1}
        )
        await self._refresh_token_service.redis.set(
            f"user_version:{user.id}",
            user.token_version,
        )
        return user

    async def on_after_reset_password(
        self,
        user: User,
        request: Optional["Request"] = None,
    ):
        await self.increment_token_version(user)
        log.info(
            "on_after_reset_password: token_version incremented user_id=%s", user.id
        )

    async def on_after_register(
        self,
        user: User,
        request: Optional["Request"] = None,
    ):
        log.warning(
            "User %r has registered.",
            user.id,
        )

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ):
        log.warning(
            "Verification requested for user %r. Verification token: %r",
            user.id,
            token,
        )

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ):
        log.warning(
            "User %r has forgot their password. Reset token: %r",
            user.id,
            token,
        )
