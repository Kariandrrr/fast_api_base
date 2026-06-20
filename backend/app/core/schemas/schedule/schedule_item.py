from datetime import date, datetime
from uuid import UUID

from pydantic import Field, BaseModel, model_validator

from .. import BaseSchema
from ..AuditResponse import AuditResponse
from ..ListResponse import ListResponse
from ....enums import ActivityType


class ScheduleItemBase(BaseSchema):
    class_date: date = Field(..., description="Дата пары/урока")
    activity_type: ActivityType = Field(
        ...,
        description="Тип пары",
        examples=["lecture", "seminar", "practical_work", "laboratory_work"],
    )

    @model_validator(mode="after")
    def validate_date(self) -> "ScheduleItemBase":
        if self.class_date < date.today():
            raise ValueError("Нельзя создавать занятия в прошлом")
        return self


class ScheduleItemCreate(ScheduleItemBase):
    group_id: UUID = Field(..., description="ID группы")
    subject_id: UUID = Field(..., description="ID предмета")
    teacher_id: UUID = Field(..., description="ID преподавателя")
    room_id: UUID = Field(..., description="ID аудитории")
    semester_id: UUID = Field(..., description="ID семестра")
    time_slot_id: UUID = Field(..., description="ID временного слота")


class ScheduleItemUpdate(BaseModel):
    group_id: UUID | None = Field(None, description="ID группы")
    subject_id: UUID | None = Field(None, description="ID предмета")
    teacher_id: UUID | None = Field(None, description="ID преподавателя")
    room_id: UUID | None = Field(None, description="ID аудитории")
    semester_id: UUID | None = Field(None, description="ID семестра")
    time_slot_id: UUID | None = Field(None, description="ID временного слота")
    class_date: date | None = Field(None, description="Дата пары/урока")
    activity_type: ActivityType | None = Field(
        None,
        description="Тип пары",
        examples=["lecture", "seminar", "practical_work", "laboratory_work"],
    )

    @model_validator(mode="after")
    def validate_date(self) -> "ScheduleItemUpdate":
        if self.class_date is not None and self.class_date < date.today():
            raise ValueError("Нельзя устанавливать дату занятия в прошлом")
        return self


class ScheduleItemBrief(BaseSchema):
    id: UUID = Field(..., description="Уникальный идентификатор")
    class_date: date = Field(..., description="Дата пары/урока")
    activity_type: ActivityType = Field(..., description="Тип пары")
    group_id: UUID = Field(..., description="ID группы")
    subject_id: UUID = Field(..., description="ID предмета")
    teacher_id: UUID = Field(..., description="ID преподавателя")


class ScheduleItemResponse(BaseSchema, ScheduleItemBase, AuditResponse):
    id: UUID = Field(..., description="Уникальный идентификатор")
    created_at: datetime
    group_id: UUID = Field(..., description="ID группы")
    subject_id: UUID = Field(..., description="ID предмета")
    teacher_id: UUID = Field(..., description="ID преподавателя")
    room_id: UUID = Field(..., description="ID аудитории")
    semester_id: UUID = Field(..., description="ID семестра")
    time_slot_id: UUID = Field(..., description="ID временного слота")


class ScheduleItemListResponse(ListResponse):
    items: list[ScheduleItemResponse]
