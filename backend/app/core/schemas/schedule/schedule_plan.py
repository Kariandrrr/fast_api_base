from uuid import UUID

from pydantic import Field, BaseModel, model_validator

from .. import BaseSchema
from ..AuditResponse import AuditResponse
from ..ListResponse import ListResponse


class SchedulePlanBase(BaseSchema):
    year: int = Field(..., ge=1, le=7, description="Год обучения")
    lecture_hours: int = Field(
        ..., gt=0, lt=1500, description="Количество лекционных часов"
    )
    practice_hours: int = Field(
        ..., ge=0, le=1500, description="Количество часов практики"
    )

    @model_validator(mode="after")
    def validate_hours(self) -> "SchedulePlanBase":
        if self.lecture_hours == 0 and self.practice_hours == 0:
            raise ValueError("Должен быть хотя бы один тип часов (лекции или практика)")
        return self


class SchedulePlanCreate(SchedulePlanBase):
    speciality_id: UUID = Field(..., description="ID специальности")
    subject_id: UUID = Field(..., description="ID предмета")
    semester_id: UUID = Field(..., description="ID семестра")


class SchedulePlanUpdate(BaseModel):
    speciality_id: UUID | None = Field(None, description="ID специальности")
    subject_id: UUID | None = Field(None, description="ID предмета")
    semester_id: UUID | None = Field(None, description="ID семестра")
    year: int | None = Field(None, ge=1, le=7, description="Год обучения")
    lecture_hours: int | None = Field(
        None, gt=0, lt=1500, description="Количество лекционных часов"
    )
    practice_hours: int | None = Field(
        None, ge=0, le=1500, description="Количество часов практики"
    )

    @model_validator(mode="after")
    def validate_hours(self) -> "SchedulePlanUpdate":
        if self.lecture_hours is not None and self.practice_hours is not None:
            if self.lecture_hours == 0 and self.practice_hours == 0:
                raise ValueError("Должен быть хотя бы один тип часов")
        return self


class SchedulePlanResponse(BaseSchema, SchedulePlanBase, AuditResponse):
    id: UUID = Field(..., description="Уникальный идентификатор")
    speciality_id: UUID = Field(..., description="ID специальности")
    subject_id: UUID = Field(..., description="ID предмета")
    semester_id: UUID = Field(..., description="ID семестра")


class SchedulePlanListResponse(ListResponse):
    items: list[SchedulePlanResponse]
