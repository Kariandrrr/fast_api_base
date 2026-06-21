from datetime import time
from uuid import UUID

from pydantic import Field, BaseModel, model_validator, field_validator

from .. import BaseSchema
from ..AuditResponse import AuditResponse
from ..ListResponse import ListResponse
from ....enums import SlotNumber


class TimeSlotBase(BaseSchema):
    slot_number: SlotNumber = Field(..., description="Номер пары/временного слота")
    start_time: time = Field(
        ...,
        description="Время начала",
    )
    end_time: time = Field(
        ...,
        description="Время окончания",
    )

    @model_validator(mode="after")
    def validate_time_range(self) -> "TimeSlotBase":
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


class TimeSlotCreate(TimeSlotBase):
    pass


class TimeSlotUpdate(BaseModel):
    slot_number: SlotNumber | None = Field(
        None, description="Номер пары/временного слота"
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
    def validate_time_range(self) -> "TimeSlotUpdate":
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


class TimeSlotResponse(BaseSchema, TimeSlotBase, AuditResponse):
    id: UUID = Field(..., description="Уникальный идентификатор")


class TimeSlotBrief(BaseSchema):
    id: UUID = Field(..., description="Уникальный идентификатор временного слота")
    slot_number: SlotNumber = Field(..., description="Номер пары/временного слота")
    start_time: time = Field(
        ...,
        description="Время начала",
    )
    end_time: time = Field(
        ...,
        description="Время окончания",
    )


class TimeSlotListResponse(ListResponse):
    items: list[TimeSlotResponse]
