from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.core.schemas import BaseSchema


class AuditResponse(BaseSchema):
    created_at: datetime = Field(..., description="Дата создания")
    created_by: UUID = Field(..., description="Кем создано (ID пользователя)")
    updated_at: datetime = Field(..., description="Дата последнего обновления")
    updated_by: UUID = Field(..., description="Кем обновлено (ID пользователя)")
