from typing import TYPE_CHECKING

from sqlalchemy import (
    UUID,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .helpers import Base
from .mixins import UUIDPKMixin

if TYPE_CHECKING:
    from . import Teacher
    from . import Subject


class TeacherSubject(Base, UUIDPKMixin):
    teacher_id: Mapped[UUID] = mapped_column(
        ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False
    )
    subject_id: Mapped[UUID] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )

    # rel
    teacher: Mapped["Teacher"] = relationship(
        "Teacher", back_populates="teacher_subjects", lazy="selectin"
    )

    subject: Mapped["Subject"] = relationship(
        "Subject", back_populates="teacher_subjects", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint(
            "teacher_id",
            "subject_id",
            name="uniq_teacher_id_subject_id_and_teacher_id",
        ),
        Index("idx_teacher_subject_teacher", "teacher_id"),
        Index("idx_teacher_subject_subject", "subject_id"),
    )
