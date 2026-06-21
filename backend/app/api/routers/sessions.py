from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_users.jwt import decode_jwt

from app.api.dependencies.authentication import fastapi_users, auth_guard
from app.core.authentication import (
    SessionService,
    get_session_service,
    RefreshTokenService,
    get_refresh_token_service,
)
from app.core.authentication.strategy import AppJWTStrategy, get_jwt_strategy
from app.core.config import settings
from app.core.models import User
from app.core.schemas import SessionRead

sessions_router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


def _session_id_from_token(strategy: AppJWTStrategy, token: str) -> str | None:
    try:
        data = decode_jwt(
            encoded_jwt=token,
            secret=strategy.decode_key,
            audience=strategy.token_audience,
            algorithms=[strategy.algorithm],
        )
        return data.get("session_id")
    except Exception:
        return None


@sessions_router.get("", response_model=list[SessionRead])
async def list_sessions(
    user_token: Annotated[
        tuple[User, str],
        Depends(fastapi_users.authenticator.current_user_token(active=True)),
    ],
    session_service: Annotated[SessionService, Depends(get_session_service)],
    strategy: Annotated[AppJWTStrategy, Depends(get_jwt_strategy)],
):
    user, token = user_token
    current_sid = _session_id_from_token(strategy, token)

    sessions = await session_service.list(str(user.id))
    for s in sessions:
        s["is_current"] = s["session_id"] == current_sid
    return sessions


@sessions_router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(
    session_id: str,
    user: Annotated[User, auth_guard],
    session_service: Annotated[SessionService, Depends(get_session_service)],
    strategy: Annotated[AppJWTStrategy, Depends(get_jwt_strategy)],
    refresh_service: Annotated[
        RefreshTokenService, Depends(get_refresh_token_service)
    ],
):
    session_data = await session_service.delete(str(user.id), session_id)
    if session_data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")

    access_jti = session_data.get("access_jti")
    refresh_jti = session_data.get("refresh_jti")
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