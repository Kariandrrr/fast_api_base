from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.crud.users import deactivate_user
from app.api.dependencies.authentication import auth_guard, fastapi_users
from app.core.config import settings
from app.core.models import db_helper, User
from app.core.schemas import UserRead, UserUpdate

users_router = APIRouter(
    prefix=settings.api.prefix.users,
    tags=[settings.api.tags.users],
)


@users_router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_own_account(
    current_user: Annotated[User, auth_guard],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    await deactivate_user(session, current_user)


users_router.include_router(
    router=fastapi_users.get_users_router(
        user_schema=UserRead,
        user_update_schema=UserUpdate,
    ),
)
