from fastapi import APIRouter

from app.core.config.main_config import settings
from .routers import router

api_router = APIRouter(prefix=settings.api.prefix.api)
api_router.include_router(router=router)
