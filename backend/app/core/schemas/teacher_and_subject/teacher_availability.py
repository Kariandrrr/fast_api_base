from datetime import time
from uuid import UUID

from pydantic import Field, BaseModel, model_validator, field_validator

from .. import BaseSchema
from ..AuditResponse import AuditResponse
from ..ListResponse import ListResponse
from ....enums import DayOfWeek


class TeacherAvailabilityBase(BaseSchema):
    day_of_week: DayOfWeek = Field(
        ...,
        description="День недели",
        examples=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    )
    start_time: time = Field(
        ...,
        description="Время начала",
    )
    end_time: time = Field(
        ...,
        description="Время окончания",
    )

    @model_validator(mode="after")
    def validate_time_range(self) -> "TeacherAvailabilityBase":
        if self.start_time >= self.end_time:
            raise ValueError(
                f"Время окончания ({self.end_time}) должно быть больше времени начала ({self.start_time})"
            )
        return self

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_precision(cls, v: time) -> time:
        if v.second != 0:
            raise ValueError(
                f"Время должно быть указано с точностью до минут, получено: {v}"
            )
        return v


class TeacherAvailabilityCreate(TeacherAvailabilityBase):
    teacher_id: UUID = Field(..., description="Уникальный идентификатор преподавателя")


class TeacherAvailabilityUpdate(BaseModel):
    day_of_week: DayOfWeek | None = Field(
        None,
        description="День недели",
        examples=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    )
    start_time: time | None = Field(
        None,
        description="Время начала",
    )
    end_time: time | None = Field(
        None,
        description="Время окончания",
    )

    @model_validator(mode="after")
    def validate_time_range(self) -> "TeacherAvailabilityUpdate":
        if self.start_time is not None and self.end_time is not None:
            if self.start_time >= self.end_time:
                raise ValueError(
                    f"Время окончания ({self.end_time}) должно быть больше времени начала ({self.start_time})"
                )
        return self

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_precision(cls, v: time | None) -> time | None:
        if v is not None and v.second != 0:
            raise ValueError(
                f"Время должно быть указано с точностью до минут, получено: {v}"
            )
        return v


class TeacherAvailabilityResponse(BaseSchema, TeacherAvailabilityBase, AuditResponse):
    id: UUID = Field(..., description="Уникальный идентификатор")
    teacher_id: UUID = Field(..., description="Уникальный идентификатор преподавателя")


class TeacherAvailabilityBrief(BaseSchema):
    id: UUID = Field(..., description="ID слота доступности")
    teacher_id: UUID = Field(..., description="Уникальный идентификатор преподавателя")
    day_of_week: DayOfWeek = Field(..., description="День недели")
    start_time: time = Field(
        ...,
        description="Время начала",
    )
    end_time: time = Field(
        ...,
        description="Время окончания",
    )


class TeacherAvailabilityListResponse(ListResponse):
    items: list[TeacherAvailabilityResponse]
