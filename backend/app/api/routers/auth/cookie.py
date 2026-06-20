from fastapi import APIRouter
from fastapi.routing import APIRoute

from app.api.dependencies.authentication.fastapi_users import fastapi_users
from app.api.routers.auth.logout import (
    make_cookie_logout_router,
    make_cookie_logout_all_router,
)
from app.api.routers.auth.refresh import make_cookie_refresh_router
from app.core.authentication import auth_cookie_backend
from app.core.config.main_config import settings
from app.core.schemas import UserRead, UserCreate

cookie_router = APIRouter(
    prefix=settings.api.prefix.cookie,
    tags=[settings.api.tags.cookie],
)

# /login /logout — FU-шный, но удаляем /logout из схемы
_fu_auth_router = fastapi_users.get_auth_router(
    backend=auth_cookie_backend,
    requires_verification=settings.auth.requires_verification,
)
_fu_auth_router.routes = [
    route
    for route in _fu_auth_router.routes
    if not (isinstance(route, APIRoute) and route.path == "/logout")
]
cookie_router.include_router(router=_fu_auth_router)

# /logout — кастомный
cookie_router.include_router(make_cookie_logout_router())

# /logout-all — кастомный
cookie_router.include_router(make_cookie_logout_all_router())

# /refresh — кастомный
cookie_router.include_router(make_cookie_refresh_router())

# /register
cookie_router.include_router(
    router=fastapi_users.get_register_router(
        user_schema=UserRead,
        user_create_schema=UserCreate,
    )
)

# /request-verify-token /verify
cookie_router.include_router(
    router=fastapi_users.get_verify_router(
        user_schema=UserRead,
    )
)

# /forgot-password /reset-password
cookie_router.include_router(router=fastapi_users.get_reset_password_router())
