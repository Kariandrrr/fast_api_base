from pydantic import Field

from app.core.schemas import BaseSchema


class ListResponse(BaseSchema):
    total: int = Field(..., ge=0, description="Всего записей")
    page: int = Field(..., ge=1, description="Текущая страница")
    size: int = Field(..., ge=1, le=100, description="Записей на странице")
    pages: int = Field(..., ge=0, description="Всего страниц")
