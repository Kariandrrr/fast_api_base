from datetime import date
from uuid import UUID

from pydantic import Field, BaseModel, model_validator

from .. import BaseSchema
from ..AuditResponse import AuditResponse
from ..ListResponse import ListResponse
from ..schedule.practice import PracticeBrief


class SemesterBase(BaseSchema):
    academic_year: int = Field(
        ...,
        ge=1,
        le=7,
        description="Академический год (1-7)",
    )
    semester_number: int = Field(
        ...,
        ge=1,
        le=14,
        description="Номер семестра (1-14)",
    )
    start_date: date = Field(
        ...,
        description="Дата начала семестра",
        examples=["2024-09-01"],
    )
    end_date: date = Field(
        ...,
        description="Дата окончания семестра",
        examples=["2025-01-15"],
    )
    session_start_date: date = Field(
        ...,
        description="Дата начала экзаменационной сессии",
        examples=["2025-01-16"],
    )
    session_end_date: date = Field(
        ...,
        description="Дата окончания экзаменационной сессии",
        examples=["2025-02-05"],
    )
    description: str | None = Field(
        None,
        max_length=150,
        description="Описание семестра",
        examples=["Осенний семестр 2024-2025 учебного года"],
    )

    @model_validator(mode="after")
    def validate_dates(self) -> "SemesterBase":
        if self.end_date <= self.start_date:
            raise ValueError(
                f"Дата окончания семестра ({self.end_date}) должна быть позже даты начала ({self.start_date})"
            )

        if self.session_start_date < self.start_date:
            raise ValueError(
                f"Сессия не может начаться раньше начала семестра. "
                f"Начало семестра: {self.start_date}, начало сессии: {self.session_start_date}"
            )

        if self.session_end_date > self.end_date:
            raise ValueError(
                f"Сессия не может закончиться позже окончания семестра. "
                f"Окончание семестра: {self.end_date}, окончание сессии: {self.session_end_date}"
            )

        if self.session_end_date <= self.session_start_date:
            raise ValueError(
                f"Дата окончания сессии ({self.session_end_date}) должна быть позже даты начала ({self.session_start_date})"
            )

        return self


class SemesterCreate(SemesterBase):
    pass


class SemesterUpdate(BaseModel):
    academic_year: int | None = Field(
        None,
        ge=1,
        le=7,
        description="Академический год (1-7)",
    )
    semester_number: int | None = Field(
        None,
        ge=1,
        le=14,
        description="Номер семестра (1-14)",
    )
    start_date: date | None = Field(
        None,
        description="Дата начала семестра",
        examples=["2024-09-01"],
    )
    end_date: date | None = Field(
        None,
        description="Дата окончания семестра",
        examples=["2025-01-15"],
    )
    session_start_date: date | None = Field(
        None,
        description="Дата начала экзаменационной сессии",
        examples=["2025-01-16"],
    )
    session_end_date: date | None = Field(
        None,
        description="Дата окончания экзаменационной сессии",
        examples=["2025-02-05"],
    )
    description: str | None = Field(
        None,
        max_length=150,
        description="Описание семестра",
        examples=["Осенний семестр 2024-2025 учебного года"],
    )

    @model_validator(mode="after")
    def validate_dates(self) -> "SemesterUpdate":
        if self.start_date is not None and self.end_date is not None:
            if self.end_date <= self.start_date:
                raise ValueError(
                    f"Дата окончания семестра ({self.end_date}) должна быть позже даты начала ({self.start_date})"
                )

        if self.start_date is not None and self.session_start_date is not None:
            if self.session_start_date < self.start_date:
                raise ValueError(f"Сессия не может начаться раньше начала семестра")

        if self.end_date is not None and self.session_end_date is not None:
            if self.session_end_date > self.end_date:
                raise ValueError(
                    f"Сессия не может закончиться позже окончания семестра"
                )

        if self.session_start_date is not None and self.session_end_date is not None:
            if self.session_end_date <= self.session_start_date:
                raise ValueError(f"Дата окончания сессии должна быть позже даты начала")

        return self


class SemesterResponse(BaseSchema, SemesterBase, AuditResponse):
    id: UUID = Field(..., description="Уникальный идентификатор")


class SemesterDetailResponse(SemesterResponse):
    practices: list[PracticeBrief] = Field(
        default_factory=list,
        description="Список практик в семестре",
    )


class SemesterBrief(BaseSchema):
    id: UUID = Field(..., description="Уникальный идентификатор")
    academic_year: int = Field(
        ...,
        description="Академический год (1-7)",
    )
    semester_number: int = Field(
        ...,
        description="Номер семестра (1-14)",
    )
    start_date: date = Field(
        ...,
        description="Дата начала семестра",
    )
    end_date: date = Field(
        ...,
        description="Дата окончания семестра",
    )
    description: str | None = Field(None)

    @property
    def display_name(self) -> str:
        return f"{self.academic_year} курс, {self.semester_number} семестр"


class SemesterListResponse(ListResponse):
    items: list[SemesterResponse]
