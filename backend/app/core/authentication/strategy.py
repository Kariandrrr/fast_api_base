import logging
import time
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import Depends
from fastapi_users import exceptions, models
from fastapi_users.authentication import JWTStrategy
from fastapi_users.jwt import decode_jwt, generate_jwt
from fastapi_users.manager import BaseUserManager
from redis.asyncio import Redis

from app.core.config.main_config import settings
from app.core.models import redis_helper, User

log = logging.getLogger(__name__)


class WorkTrackJWTStrategy(JWTStrategy):
    def __init__(self, redis: Redis, **kwargs):
        super().__init__(**kwargs)
        self.redis = redis

    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[models.UP, models.ID],
    ) -> models.UP | None:
        if token is None:
            return None

        try:
            data = decode_jwt(
                encoded_jwt=token,
                secret=self.decode_key,
                audience=self.token_audience,
                algorithms=[self.algorithm],
            )
        except jwt.PyJWTError as e:
            log.warning("read_token: не удалось декодировать токен: %s", e)
            return None

        jti = data.get("jti")
        user_id = data.get("sub")
        token_version = data.get("token_version")

        if user_id is None:
            log.warning("read_token: токен не содержит sub")
            return None

        if jti and await self.redis.exists(f"blacklist:access:{jti}"):
            log.warning("read_token: токен в блэклисте jti=%s", jti)
            return None

        if token_version is not None:
            current_version = await self.redis.get(f"user_version:{user_id}")
            if current_version is not None and int(current_version) != token_version:
                log.warning("read_token: версия токена устарела user_id=%s", user_id)
                return None

        try:
            parsed_id = user_manager.parse_id(user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            log.warning("read_token: пользователь не найден user_id=%s", user_id)
            return None

    async def write_token(self, user: User) -> str:
        data = {
            "sub": str(user.id),
            "aud": self.token_audience,
            "jti": str(uuid4()),
            "token_version": user.token_version,
        }
        return generate_jwt(
            data=data,
            secret=self.encode_key,
            lifetime_seconds=self.lifetime_seconds,
            algorithm=self.algorithm,
        )

    async def destroy_token(self, token: str | None) -> None:
        if not token:
            return
        try:
            data = decode_jwt(
                encoded_jwt=token,
                secret=self.decode_key,
                audience=self.token_audience,
                algorithms=[self.algorithm],
            )
            jti = data.get("jti")
            exp = data.get("exp")
            if jti and exp:
                ttl = int(exp) - int(time.time())
                if ttl > 0:
                    await self.redis.setex(f"blacklist:access:{jti}", ttl, "1")
        except jwt.PyJWTError as e:
            log.warning("destroy_token: не удалось декодировать токен: %s", e)

    async def rotate(self, old_token: str, user: User) -> str:
        await self.destroy_token(old_token)
        return await self.write_token(user)


async def get_jwt_strategy(
    redis: Annotated[Redis, Depends(redis_helper.client_getter)],
) -> WorkTrackJWTStrategy:
    return WorkTrackJWTStrategy(
        redis=redis,
        secret=settings.auth.jwt.private_key_path.read_text(),
        lifetime_seconds=settings.auth.jwt.access_token_lifetime_seconds,
        token_audience=[settings.auth.jwt.access_token_audience],
        algorithm=settings.auth.jwt.algorithm,
        public_key=settings.auth.jwt.public_key_path.read_text(),
    )
