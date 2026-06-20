from fastapi import APIRouter
from fastapi.routing import APIRoute

from app.api.dependencies.authentication.fastapi_users import fastapi_users
from app.api.routers.auth.logout import (
    make_bearer_logout_router,
    make_bearer_logout_all_router,
)
from app.api.routers.auth.refresh import make_bearer_refresh_router
from app.core.authentication import auth_bearer_backend
from app.core.config.main_config import settings
from app.core.schemas import UserRead, UserCreate

bearer_router = APIRouter(
    prefix=settings.api.prefix.bearer,
    tags=[settings.api.tags.bearer],
)


# /login /logout — FU-шный, но удаляем /logout из схемы
_fu_auth_router = fastapi_users.get_auth_router(
    backend=auth_bearer_backend,
    requires_verification=settings.auth.requires_verification,
)
_fu_auth_router.routes = [
    route
    for route in _fu_auth_router.routes
    if not (isinstance(route, APIRoute) and route.path == "/logout")
]
bearer_router.include_router(router=_fu_auth_router)

# /logout — кастомный
bearer_router.include_router(make_bearer_logout_router())

# /logout-all — кастомный
bearer_router.include_router(make_bearer_logout_all_router())

# /refresh — кастомный
bearer_router.include_router(make_bearer_refresh_router())

# /register
bearer_router.include_router(
    router=fastapi_users.get_register_router(
        user_schema=UserRead,
        user_create_schema=UserCreate,
    )
)

# /request-verify-token /verify
bearer_router.include_router(
    router=fastapi_users.get_verify_router(
        user_schema=UserRead,
    )
)

# /forgot-password /reset-password
bearer_router.include_router(router=fastapi_users.get_reset_password_router())
