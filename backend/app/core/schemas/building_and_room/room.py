from uuid import UUID

from pydantic import Field, BaseModel

from .. import BaseSchema
from ..AuditResponse import AuditResponse
from ..ListResponse import ListResponse
from ....enums import RoomType


class RoomBase(BaseSchema):
    room_number: str = Field(
        ...,
        min_length=1,
        max_length=20,
        pattern=r"^[0-9А-ЯA-Zа-яa-z/_-]+$",
        description="Номер аудитории (примеры: 203, 203/1, 203А, 103-бис)",
    )
    capacity: int = Field(..., gt=0, description="Вместимость аудитории")
    room_type: RoomType = Field(
        default=RoomType.common_class, description="Тип аудитории"
    )


class RoomCreate(RoomBase):
    building_id: UUID = Field(..., description="ID здания")


class RoomUpdate(BaseModel):
    room_number: str | None = Field(
        None,
        min_length=1,
        max_length=20,
        pattern=r"^[0-9А-ЯA-Zа-яa-z/_-]+$",
        description="Номер аудитории (примеры: 203, 203/1, 203А, 103-бис)",
    )
    capacity: int | None = Field(None, gt=0, description="Вместимость аудитории")
    room_type: RoomType | None = Field(None, description="Тип аудитории")
    building_id: UUID | None = Field(None, description="ID здания")


class RoomResponse(BaseSchema, RoomBase, AuditResponse):
    id: UUID = Field(..., description="Уникальный идентификатор")
    building_id: UUID = Field(..., description="ID здания")


class RoomBrief(BaseSchema):
    id: UUID = Field(..., description="ID аудитории")
    room_number: str = Field(..., description="Номер аудитории")
    capacity: int = Field(..., description="Вместимость")
    room_type: RoomType = Field(..., description="Тип аудитории")
    building_id: UUID | None = Field(None, description="ID здания")


class RoomListResponse(ListResponse):
    items: list[RoomResponse]
