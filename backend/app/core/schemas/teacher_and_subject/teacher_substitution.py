from datetime import datetime
from uuid import UUID

from pydantic import Field, BaseModel

from .teacher import TeacherBrief
from .. import BaseSchema, ScheduleItemBrief
from ..AuditResponse import AuditResponse
from ..ListResponse import ListResponse


class TeacherSubstitutionBase(BaseSchema):
    reason: str = Field(..., max_length=100, description="Причина замены")


class TeacherSubstitutionCreate(TeacherSubstitutionBase):
    schedule_item_id: UUID = Field(..., description="ID пары/урока")
    old_teacher_id: UUID = Field(..., description="ID замененного преподавателя")
    new_teacher_id: UUID = Field(..., description="ID преподавателя на замене")


class TeacherSubstitutionUpdate(BaseModel):
    schedule_item_id: UUID | None = Field(None, description="ID пары/урока")
    old_teacher_id: UUID | None = Field(
        None, description="ID замененного преподавателя"
    )
    new_teacher_id: UUID | None = Field(None, description="ID преподавателя на замене")
    reason: str | None = Field(None, max_length=100, description="Причина замены")


class TeacherSubstitutionResponse(BaseSchema, TeacherSubstitutionBase, AuditResponse):
    id: UUID = Field(..., description="Уникальный идентификатор")
    schedule_item_id: UUID = Field(..., description="ID пары/урока")
    old_teacher_id: UUID = Field(..., description="ID замененного преподавателя")
    new_teacher_id: UUID = Field(..., description="ID преподавателя на замене")
    created_at: datetime = Field(..., description="Дата и время создания записи")


class TeacherSubstitutionDetailResponse(TeacherSubstitutionResponse):
    schedule_item: ScheduleItemBrief
    old_teacher: TeacherBrief
    new_teacher: TeacherBrief


class TeacherSubstitutionListResponse(ListResponse):
    items: list[TeacherSubstitutionResponse]
