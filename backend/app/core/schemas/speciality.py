from uuid import UUID

from pydantic import Field, BaseModel

from . import BaseSchema
from .ListResponse import ListResponse
from .teacher_and_subject.teacher import TeacherBrief


class SpecialityBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=70, description="Название специальности")
    code: str = Field(..., min_length=1, max_length=20, description="Код специальности")


class SpecialityCreate(SpecialityBase):
    pass


class SpecialityUpdate(BaseModel):
    name: str | None = Field(
        None, min_length=1, max_length=70, description="Название специальности"
    )
    code: str | None = Field(
        None, min_length=1, max_length=20, description="Код специальности"
    )


class SpecialityResponse(BaseSchema, SpecialityBase):
    id: UUID = Field(..., description="Уникальный идентификатор")


class SpecialityDetailResponse(SpecialityResponse):
    teachers: list[TeacherBrief] = Field(
        default_factory=list,
        description="Список преподавателей на направлении",
    )


class SpecialityBrief(BaseSchema):
    id: UUID = Field(..., description="ID специальности")
    name: str = Field(..., description="Название специальности")
    code: str = Field(..., description="Код специальности")


class SubjectListResponse(ListResponse):
    items: list[SpecialityResponse]
