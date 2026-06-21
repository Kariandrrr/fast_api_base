from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi_users.jwt import decode_jwt
from pydantic import BaseModel

from app.api.dependencies.authentication import fastapi_users, auth_guard
from app.api.dependencies.authentication.user_manager import get_user_manager
from app.core.authentication import (
    RefreshTokenService,
    get_refresh_token_service,
    SessionService,
    get_session_service,
    UserManager,
)
from app.core.authentication.strategy import AppJWTStrategy, get_jwt_strategy
from app.core.config import settings
from app.core.models import User


class BearerLogoutSchema(BaseModel):
    refresh_token: str


def _extract_session_id(strategy: AppJWTStrategy, token: str | None) -> tuple[str | None, str | None]:
    if not token:
        return None, None
    try:
        data = decode_jwt(
            encoded_jwt=token,
            secret=strategy.decode_key,
            audience=strategy.token_audience,
            algorithms=[strategy.algorithm],
        )
        return data.get("sub"), data.get("session_id")
    except Exception:
        return None, None


def make_cookie_logout_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "/logout", status_code=status.HTTP_204_NO_CONTENT, dependencies=[auth_guard]
    )
    async def cookie_logout(
        request: Request,
        response: Response,
        strategy: Annotated[AppJWTStrategy, Depends(get_jwt_strategy)],
        refresh_service: Annotated[
            RefreshTokenService, Depends(get_refresh_token_service)
        ],
        session_service: Annotated[SessionService, Depends(get_session_service)],
    ):
        access_token = request.cookies.get(settings.auth.cookie.access_name)
        refresh_token = request.cookies.get(settings.auth.cookie.refresh_name)

        user_id, session_id = _extract_session_id(strategy, access_token)
        if user_id and session_id:
            await session_service.delete(user_id, session_id)

        if access_token:
            await strategy.destroy_token(access_token)
        if refresh_token:
            await refresh_service.destroy_token(refresh_token)

        response.delete_cookie(
            key=settings.auth.cookie.access_name,
            path=settings.auth.cookie.path,
        )
        response.delete_cookie(
            key=settings.auth.cookie.refresh_name,
            path=settings.auth.cookie.refresh_path,
        )

    return router


def make_bearer_logout_router() -> APIRouter:
    router = APIRouter()

    @router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
    async def bearer_logout(
        body: BearerLogoutSchema,
        user_token: Annotated[
            tuple[User, str],
            Depends(fastapi_users.authenticator.current_user_token(active=True)),
        ],
        strategy: Annotated[AppJWTStrategy, Depends(get_jwt_strategy)],
        refresh_service: Annotated[
            RefreshTokenService, Depends(get_refresh_token_service)
        ],
        session_service: Annotated[SessionService, Depends(get_session_service)],
    ):
        access_token: str = user_token[1]

        user_id, session_id = _extract_session_id(strategy, access_token)
        if user_id and session_id:
            await session_service.delete(user_id, session_id)

        await strategy.destroy_token(access_token)
        await refresh_service.destroy_token(body.refresh_token)

    return router


async def _blacklist_sessions(
    sessions: list[dict],
    strategy: AppJWTStrategy,
    refresh_service: RefreshTokenService,
) -> None:
    for s in sessions:
        access_jti = s.get("access_jti")
        refresh_jti = s.get("refresh_jti")
        if access_jti:
            await strategy.redis.set(
                f"blacklist:access:{access_jti}",
                "1",
                ex=settings.auth.jwt.access_token_lifetime_seconds,
            )
        if refresh_jti:
            await refresh_service.redis.set(
                f"blacklist:refresh:{refresh_jti}",
                "1",
                ex=settings.auth.jwt.refresh_token_lifetime_seconds,
            )


def make_cookie_logout_all_router() -> APIRouter:
    router = APIRouter()

    @router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
    async def cookie_logout_all(
        response: Response,
        user: Annotated[User, auth_guard],
        user_manager: Annotated[UserManager, Depends(get_user_manager)],
        session_service: Annotated[SessionService, Depends(get_session_service)],
        strategy: Annotated[AppJWTStrategy, Depends(get_jwt_strategy)],
        refresh_service: Annotated[
            RefreshTokenService, Depends(get_refresh_token_service)
        ],
    ):
        sessions = await session_service.delete_all(str(user.id))
        await _blacklist_sessions(sessions, strategy, refresh_service)
        await user_manager.increment_token_version(user)

        response.delete_cookie(
            key=settings.auth.cookie.access_name,
            path=settings.auth.cookie.path,
        )
        response.delete_cookie(
            key=settings.auth.cookie.refresh_name,
            path=settings.auth.cookie.refresh_path,
        )

    return router


def make_bearer_logout_all_router() -> APIRouter:
    router = APIRouter()

    @router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
    async def bearer_logout_all(
        user: Annotated[User, auth_guard],
        user_manager: Annotated[UserManager, Depends(get_user_manager)],
        session_service: Annotated[SessionService, Depends(get_session_service)],
        strategy: Annotated[AppJWTStrategy, Depends(get_jwt_strategy)],
        refresh_service: Annotated[
            RefreshTokenService, Depends(get_refresh_token_service)
        ],
    ):
        sessions = await session_service.delete_all(str(user.id))
        await _blacklist_sessions(sessions, strategy, refresh_service)
        await user_manager.increment_token_version(user)

    return router