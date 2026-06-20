from datetime import time, date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Time,
    CheckConstraint,
    Date,
    UniqueConstraint,
    String,
    ForeignKey,
    Boolean,
    Index,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .helpers import Base
from .mixins import (
    UUIDPKMixin,
    CreatedByMixin,
    TimestampMixin,
    UpdateAtMixin,
    UpdatedByMixin,
)
from ...enums import DayOfWeek

if TYPE_CHECKING:
    from . import TeacherSubject
    from . import ScheduleItem
    from . import Subject


class Teacher(
    Base, UUIDPKMixin, TimestampMixin, CreatedByMixin, UpdateAtMixin, UpdatedByMixin
):
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(30), nullable=True)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)

    is_full_time: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_invited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    hired_date: Mapped[date] = mapped_column(Date, nullable=False)

    # rel
    teacher_subjects: Mapped[list["TeacherSubject"]] = relationship(
        "TeacherSubject",
        back_populates="teacher",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    availabilities: Mapped[list["TeacherAvailability"]] = relationship(
        "TeacherAvailability",
        back_populates="teacher",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    schedule_items: Mapped[list["ScheduleItem"]] = relationship(
        "ScheduleItem", back_populates="teacher", lazy="selectin"
    )

    substitutions_as_old: Mapped[list["TeacherSubstitution"]] = relationship(
        "TeacherSubstitution",
        foreign_keys="[TeacherSubstitution.old_teacher_id]",
        back_populates="old_teacher",
        lazy="selectin",
    )

    substitutions_as_new: Mapped[list["TeacherSubstitution"]] = relationship(
        "TeacherSubstitution",
        foreign_keys="[TeacherSubstitution.new_teacher_id]",
        back_populates="new_teacher",
        lazy="selectin",
    )

    @property
    def subjects(self) -> list["Subject"]:
        # return the list of subjects taught by the teacher
        return [ts.subject for ts in self.teacher_subjects]

    __table_args__ = (
        CheckConstraint(
            "NOT (is_full_time = TRUE AND is_invited = TRUE)",
            name="check_teacher_status",
        ),
    )


class TeacherAvailability(
    Base, UUIDPKMixin, TimestampMixin, CreatedByMixin, UpdateAtMixin, UpdatedByMixin
):
    __tablename__ = "teacher_availability"

    teacher_id: Mapped[UUID] = mapped_column(ForeignKey("teachers.id"), nullable=False)

    day_of_week: Mapped[DayOfWeek] = mapped_column(
        ENUM(DayOfWeek, name="day_of_week", create_type=True), nullable=False
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    # rel
    teacher: Mapped["Teacher"] = relationship(
        "Teacher",
        back_populates="availabilities",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint(
            "end_time > start_time", name="check_time_order_in_availability"
        ),
        UniqueConstraint(
            "teacher_id", "day_of_week", "start_time", name="uq_teacher_day_time"
        ),
        # search available teachers in certain day+time
        Index(
            "idx_teacher_availability_day_time", "day_of_week", "start_time", "end_time"
        ),
        # search all slots of prof
        Index("idx_teacher_availability_teacher", "teacher_id"),
    )


class TeacherSubstitution(
    Base, UUIDPKMixin, TimestampMixin, CreatedByMixin, UpdateAtMixin, UpdatedByMixin
):
    schedule_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("schedule_items.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    old_teacher_id: Mapped[UUID] = mapped_column(
        ForeignKey("teachers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    new_teacher_id: Mapped[UUID] = mapped_column(
        ForeignKey("teachers.id", ondelete="RESTRICT"),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(String(100), nullable=True)

    # rel
    schedule_item: Mapped["ScheduleItem"] = relationship(
        "ScheduleItem", back_populates="substitution", lazy="selectin"
    )

    old_teacher: Mapped["Teacher"] = relationship(
        "Teacher",
        foreign_keys=[old_teacher_id],
        back_populates="substitutions_as_old",
        lazy="selectin",
    )

    new_teacher: Mapped["Teacher"] = relationship(
        "Teacher",
        foreign_keys=[new_teacher_id],
        back_populates="substitutions_as_new",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint(
            "old_teacher_id != new_teacher_id",
            name="ck_teacher_substitution_diff_teachers",
        ),
        CheckConstraint(
            "reason IS NULL OR length(trim(reason)) > 0",
            name="ck_teacher_substitution_reason_not_empty",
        ),
        Index("idx_teacher_substitution_schedule_item", "schedule_item_id"),
        Index("idx_teacher_substitution_old_teacher", "old_teacher_id"),
        Index("idx_teacher_substitution_new_teacher", "new_teacher_id"),
        Index("idx_teacher_substitution_created_at", "created_at"),
    )
