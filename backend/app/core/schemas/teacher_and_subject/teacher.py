from datetime import date
from uuid import UUID

from pydantic import Field, BaseModel, EmailStr, field_validator

from .subject import SubjectBrief
from .. import BaseSchema
from ..AuditResponse import AuditResponse
from ..ListResponse import ListResponse


class TeacherBase(BaseSchema):
    name: str = Field(
        ...,
        description="Имя",
        min_length=1,
        max_length=50,
        pattern=r"^[A-ZА-Я][a-zа-яA-ZА-Я-]*$",
    )
    middle_name: str | None = Field(
        None,
        description="Отчетсво/второе имя",
        min_length=1,
        max_length=50,
        pattern=r"^[A-ZА-Я][a-zа-яA-ZА-Я-]*$",
    )
    last_name: str = Field(
        ...,
        description="Фамилия",
        min_length=1,
        max_length=50,
        pattern=r"^[A-ZА-Я][a-zа-яA-ZА-Я-]*$",
    )
    is_full_time: bool = Field(..., description="Штатный сотрудник")
    is_invited: bool = Field(..., description="Приглашенный")
    phone: str = Field(
        ...,
        description="Номер телефона",
        min_length=10,
        max_length=20,
        pattern=r"^\+?[0-9\s\-()]+$",
        examples=["+7 (123) 456-78-90", "8-123-456-78-90"],
    )
    email: EmailStr = Field(..., description="Email")
    hired_date: date = Field(
        ...,
        description="Дата приема на работу",
        examples=["2023-09-01"],
    )

    @field_validator("name", "middle_name", "last_name")
    @classmethod
    def validate_name_parts(cls, v: str | None) -> str | None:
        if v is not None:
            if "  " in v:
                raise ValueError("Не допускаются множественные пробелы")
            if any(c.isdigit() for c in v):
                raise ValueError("Имя не может содержать цифры")
            return v[0].upper() + v[1:].lower() if len(v) > 1 else v.upper()
        return v


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdateByAdmin(BaseModel):
    name: str | None = Field(
        None,
        description="Имя",
        min_length=1,
        max_length=50,
        pattern=r"^[A-ZА-Я][a-zа-яA-ZА-Я-]*$",
    )
    middle_name: str | None = Field(
        None,
        description="Отчетсво/второе имя",
        min_length=1,
        max_length=50,
        pattern=r"^[A-ZА-Я][a-zа-яA-ZА-Я-]*$",
    )
    last_name: str | None = Field(
        None,
        description="Фамилия",
        min_length=1,
        max_length=50,
        pattern=r"^[A-ZА-Я][a-zа-яA-ZА-Я-]*$",
    )
    is_full_time: bool | None = Field(None, description="Штатный сотрудник")
    is_invited: bool | None = Field(None, description="Приглашенный сотрудник")
    phone: str | None = Field(
        None,
        description="Номер телефона",
        min_length=10,
        max_length=20,
        pattern=r"^\+?[0-9\s\-()]+$",
        examples=["+7 (123) 456-78-90", "8-123-456-78-90"],
    )
    email: EmailStr | None = Field(None, description="Email")
    hired_date: date | None = Field(
        None,
        description="Дата приема на работу",
        examples=["2023-09-01"],
    )


class TeacherUpdateByTeacher(BaseModel):
    phone: str | None = Field(
        None,
        description="Номер телефона",
        min_length=10,
        max_length=20,
        pattern=r"^\+?[0-9\s\-()]+$",
        examples=["+7 (123) 456-78-90", "8-123-456-78-90"],
    )
    email: EmailStr | None = Field(None, description="Email")


class TeacherResponse(BaseSchema, TeacherBase, AuditResponse):
    id: UUID = Field(..., description="Уникальный идентификатор")


class TeacherDetailResponse(TeacherResponse):
    subjects: list[SubjectBrief] = Field(
        default_factory=list,
        description="Список предметов, которые ведёт преподаватель",
    )


class TeacherBrief(BaseSchema):
    id: UUID = Field(..., description="Уникальный идентификатор")
    name: str = Field(
        ...,
        description="Имя",
    )
    middle_name: str | None = Field(
        None,
        description="Отчетсво/второе имя",
    )
    last_name: str = Field(
        ...,
        description="Фамилия",
    )
    is_full_time: bool | None = Field(None, description="Штатный сотрудник")

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)


class TeacherListResponse(ListResponse):
    items: list[TeacherResponse]
