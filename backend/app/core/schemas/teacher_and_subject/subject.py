from uuid import UUID

from pydantic import Field, BaseModel

from .teacher import TeacherBrief
from .. import BaseSchema
from ..AuditResponse import AuditResponse
from ..ListResponse import ListResponse


class SubjectBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=70, description="Название предмета")
    code: str = Field(..., min_length=1, max_length=20, description="Код предмета")


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: str | None = Field(
        None, min_length=1, max_length=70, description="Название предмета"
    )
    code: str | None = Field(
        None, min_length=1, max_length=20, description="Код предмета"
    )


class SubjectResponse(BaseSchema, SubjectBase, AuditResponse):
    id: UUID = Field(..., description="Уникальный идентификатор")


class SubjectDetailResponse(SubjectResponse):
    teachers: list[TeacherBrief] = Field(
        default_factory=list,
        description="Список преподавателей, которые ведут предмет",
    )


class SubjectBrief(BaseSchema):
    id: UUID = Field(..., description="ID предмета")
    name: str = Field(..., description="Название предмета")
    code: str = Field(..., description="Код предмета")


class SubjectListResponse(ListResponse):
    items: list[SubjectResponse]
