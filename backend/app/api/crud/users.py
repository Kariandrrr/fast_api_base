from sqlalchemy.ext.asyncio import AsyncSession

from ...core.models import User


async def deactivate_user(session: AsyncSession, user: User) -> None:
    user.is_active = False
    await session.commit()
