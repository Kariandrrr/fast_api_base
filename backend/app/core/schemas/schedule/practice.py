from datetime import date
from uuid import UUID

from pydantic import Field, BaseModel, model_validator

from .. import BaseSchema, GroupBrief
from ..ListResponse import ListResponse
from ....enums import PracticeType
from ..AuditResponse import AuditResponse


class PracticeBase(BaseSchema):
    type: PracticeType = Field(
        default=PracticeType.educational, description="Тип практики"
    )
    practice_start_date: date = Field(
        ...,
        description="Дата начала практики",
        examples=["2024-09-01"],
    )
    practice_end_date: date = Field(
        ...,
        description="Дата окончания практики",
        examples=["2025-01-15"],
    )
    hours: int = Field(..., gt=0, lt=1000, description="Общее количество практики")

    @model_validator(mode="after")
    def validate_dates(self) -> "PracticeBase":
        if self.practice_end_date <= self.practice_start_date:
            raise ValueError(
                f"Дата окончания практики ({self.practice_end_date}) должна быть позже даты начала ({self.practice_start_date})"
            )
        if (self.practice_end_date - self.practice_start_date).days > 365:
            raise ValueError("Практика не может длиться больше года")
        return self


class PracticeCreate(PracticeBase):
    semester_id: UUID = Field(..., description="ID семестра")


class PracticeUpdate(BaseModel):
    type: PracticeType | None = Field(None, description="Тип практики")
    practice_start_date: date | None = Field(
        None,
        description="Дата начала практики",
        examples=["2024-09-01"],
    )
    practice_end_date: date | None = Field(
        None,
        description="Дата окончания практики",
        examples=["2025-01-15"],
    )
    hours: int | None = Field(
        None, gt=0, lt=1000, description="Общее количество практики"
    )

    @model_validator(mode="after")
    def validate_dates(self) -> "PracticeUpdate":
        if self.practice_start_date is not None and self.practice_end_date is not None:
            if self.practice_end_date <= self.practice_start_date:
                raise ValueError(
                    f"Дата окончания практики ({self.practice_end_date}) должна быть позже даты начала ({self.practice_start_date})"
                )
            if (self.practice_end_date - self.practice_start_date).days > 365:
                raise ValueError("Практика не может длиться больше года")
        return self


class PracticeResponse(BaseSchema, PracticeBase, AuditResponse):
    id: UUID = Field(..., description="Уникальный идентификатор")
    semester_id: UUID = Field(..., description="ID семестра")


class PracticeDetailResponse(PracticeResponse):
    groups: list[GroupBrief] = Field(
        default_factory=list,
        description="Группы, у которых есть практика",
    )


class PracticeBrief(BaseSchema):
    id: UUID = Field(..., description="Уникальный идентификатор практики")
    type: PracticeType = Field(..., description="Тип практики")
    practice_start_date: date = Field(..., description="Дата начала практики")
    practice_end_date: date = Field(..., description="Дата окончания практики")
    hours: int = Field(..., description="Количество часов")


class PracticeListResponse(ListResponse):
    items: list[PracticeResponse]
