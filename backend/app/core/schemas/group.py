from uuid import UUID

from pydantic import Field, BaseModel, computed_field

from . import BaseSchema, SpecialityResponse
from .AuditResponse import AuditResponse
from .ListResponse import ListResponse
from .teacher_and_subject.teacher import TeacherBrief
from ...enums import Shift


class GroupBase(BaseSchema):
    name: str = Field(
        ...,
        min_length=1,
        max_length=10,
        pattern=r"^[А-ЯA-Z0-9-]+$",
        description="Группа",
    )
    year: int = Field(..., ge=1, le=7, description="Год обучения")
    shift: Shift = Field(..., description="Смена обучения (первая/вторая)")
    student_count: int = Field(
        ..., ge=1, le=40, description="Количество студентов в группе"
    )


class GroupCreate(GroupBase):
    speciality_id: UUID = Field(..., description="ID специальности")
    current_semester_id: UUID = Field(..., description="ID текущего семестра")


class GroupUpdate(BaseModel):
    name: str | None = Field(
        None,
        min_length=1,
        max_length=10,
        pattern=r"^[А-ЯA-Z0-9-]+$",
        description="Группа",
    )
    year: int | None = Field(None, ge=1, le=7, description="Год обучения")
    shift: Shift | None = Field(None, description="Смена обучения (первя/вторая)")
    student_count: int | None = Field(
        None, ge=1, le=40, description="Количество студентов в группе"
    )
    speciality_id: UUID | None = Field(None, description="ID специальности")
    current_semester_id: UUID | None = Field(None, description="ID текущего семестра")


class GroupResponse(BaseSchema, GroupBase, AuditResponse):
    id: UUID = Field(..., description="Уникальный идентификатор")
    speciality_id: UUID = Field(..., description="ID специальности")
    current_semester_id: UUID = Field(..., description="ID текущего семестра")


class GroupDetailResponse(GroupResponse):
    speciality: SpecialityResponse
    teachers: list[TeacherBrief] = Field(default_factory=list)

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.name} ({self.speciality.code if hasattr(self, 'speciality') else self.speciality_id})"


class GroupBrief(BaseSchema):
    id: UUID = Field(..., description="ID группы")
    name: str = Field(..., description="Название группы")
    year: int = Field(..., description="Курс")
    shift: Shift = Field(..., description="Смена")


class GroupListResponse(ListResponse):
    items: list[GroupResponse]
