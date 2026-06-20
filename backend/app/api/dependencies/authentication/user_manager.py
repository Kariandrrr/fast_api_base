from typing import Annotated, TYPE_CHECKING

from fastapi import Depends

from app.core.authentication import (
    UserManager,
    get_refresh_token_service,
    get_session_service,
)
from app.core.authentication.strategy import AppJWTStrategy, get_jwt_strategy

from ..users import get_users_db

if TYPE_CHECKING:
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
    from app.core.authentication import RefreshTokenService, SessionService


async def get_user_manager(
    users_db: Annotated[
        "SQLAlchemyUserDatabase",
        Depends(get_users_db),
    ],
    refresh_token_service: Annotated[
        "RefreshTokenService",
        Depends(get_refresh_token_service),
    ],
    session_service: Annotated[
        "SessionService",
        Depends(get_session_service),
    ],
    strategy: Annotated[
        AppJWTStrategy,
        Depends(get_jwt_strategy),
    ],
):
    yield UserManager(
        user_db=users_db,
        refresh_token_service=refresh_token_service,
        session_service=session_service,
        strategy=strategy,
    )
