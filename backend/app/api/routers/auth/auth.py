from fastapi import APIRouter

from app.core.config.main_config import settings
from .bearer import bearer_router
from .cookie import cookie_router

auth_router = APIRouter(
    prefix=settings.api.prefix.auth,
    tags=[settings.api.tags.auth],
)

auth_router.include_router(router=cookie_router)
auth_router.include_router(router=bearer_router)
