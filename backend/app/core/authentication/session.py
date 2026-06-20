from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from user_agents import parse as parse_ua

from app.core.config.main_config import settings
from app.core.models import redis_helper

log = logging.getLogger(__name__)


def _parse_user_agent(ua_string: str) -> dict:
    ua = parse_ua(ua_string)
    if ua.is_mobile:
        device = "mobile"
    elif ua.is_tablet:
        device = "tablet"
    else:
        device = "desktop"
    browser = f"{ua.browser.family} {ua.browser.version_string}".strip()
    os_name = f"{ua.os.family} {ua.os.version_string}".strip()
    return {"device": device, "browser": browser, "os": os_name}


class SessionService:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self._ttl = settings.auth.jwt.refresh_token_lifetime_seconds

    def _key(self, user_id: str, session_id: str) -> str:
        return f"session:{user_id}:{session_id}"

    async def create(
        self,
        user_id: str,
        session_id: str,
        access_jti: str,
        refresh_jti: str,
        user_agent: str,
        ip: str,
    ) -> None:
        ua_info = _parse_user_agent(user_agent)
        now = datetime.now(timezone.utc).isoformat()
        data = {
            "device": ua_info["device"],
            "browser": ua_info["browser"],
            "os": ua_info["os"],
            "ip": ip,
            "created_at": now,
            "last_active": now,
            "access_jti": access_jti,
            "refresh_jti": refresh_jti,
        }
        await self.redis.set(
            self._key(user_id, session_id),
            json.dumps(data),
            ex=self._ttl,
        )

    async def update_jtis(
        self,
        user_id: str,
        session_id: str,
        access_jti: str,
        refresh_jti: str,
    ) -> None:
        key = self._key(user_id, session_id)
        raw = await self.redis.get(key)
        if raw is None:
            return
        data = json.loads(raw)
        data["access_jti"] = access_jti
        data["refresh_jti"] = refresh_jti
        data["last_active"] = datetime.now(timezone.utc).isoformat()
        await self.redis.set(key, json.dumps(data), ex=self._ttl)

    async def get(self, user_id: str, session_id: str) -> dict | None:
        raw = await self.redis.get(self._key(user_id, session_id))
        if raw is None:
            return None
        data = json.loads(raw)
        data["session_id"] = session_id
        return data

    async def delete(self, user_id: str, session_id: str) -> dict | None:
        key = self._key(user_id, session_id)
        raw = await self.redis.get(key)
        if raw is None:
            return None
        await self.redis.delete(key)
        data = json.loads(raw)
        data["session_id"] = session_id
        return data

    async def list(self, user_id: str) -> list[dict]:
        prefix = f"session:{user_id}:"
        sessions = []
        async for key in self.redis.scan_iter(match=f"{prefix}*"):
            raw = await self.redis.get(key)
            if raw is None:
                continue
            data = json.loads(raw)
            sid = key.decode() if isinstance(key, bytes) else key
            data["session_id"] = sid.removeprefix(prefix)
            sessions.append(data)
        return sessions

    async def delete_all(self, user_id: str) -> list[dict]:
        prefix = f"session:{user_id}:"
        sessions = []
        keys_to_delete = []
        async for key in self.redis.scan_iter(match=f"{prefix}*"):
            raw = await self.redis.get(key)
            if raw is not None:
                data = json.loads(raw)
                sid = key.decode() if isinstance(key, bytes) else key
                data["session_id"] = sid.removeprefix(prefix)
                sessions.append(data)
            keys_to_delete.append(key)
        if keys_to_delete:
            await self.redis.delete(*keys_to_delete)
        return sessions

    async def exists(self, user_id: str, session_id: str) -> bool:
        return bool(await self.redis.exists(self._key(user_id, session_id)))


async def get_session_service(
    redis: Annotated[Redis, Depends(redis_helper.client_getter)],
) -> SessionService:
    return SessionService(redis=redis)