from typing import TYPE_CHECKING

from sqlalchemy import (
    Integer,
    UniqueConstraint,
    UUID,
    ForeignKey,
    CheckConstraint,
    Date,
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
from ...enums import ActivityType

if TYPE_CHECKING:
    from . import Speciality
    from . import Subject
    from . import Semester
    from . import Group
    from . import Teacher
    from . import Room
    from . import TimeSlot
    from . import TeacherSubstitution


class SchedulePlan(
    Base, UUIDPKMixin, TimestampMixin, CreatedByMixin, UpdateAtMixin, UpdatedByMixin
):
    speciality_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "specialities.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    subject_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "subjects.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    semester_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "semesters.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    lecture_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    practice_hours: Mapped[int] = mapped_column(Integer, nullable=False)

    # rel
    speciality: Mapped["Speciality"] = relationship(
        "Speciality", back_populates="schedule_plans", lazy="selectin"
    )

    subject: Mapped["Subject"] = relationship(
        "Subject", back_populates="schedule_plans", lazy="selectin"
    )

    semester: Mapped["Semester"] = relationship(
        "Semester", back_populates="schedule_plans", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint("year BETWEEN 1 AND 7", name="ck_schedule_plan_year_range"),
        CheckConstraint(
            "lecture_hours > 0 AND lecture_hours <= 2000",
            name="ck_lecture_hours_range",
        ),
        CheckConstraint(
            "practice_hours > 0 AND practice_hours <= 1000",
            name="ck_practice_hours_range",
        ),
        CheckConstraint(
            "lecture_hours > 0 OR practice_hours > 0",
            name="ck_at_least_one_hour_type",
        ),
        UniqueConstraint(
            "speciality_id",
            "subject_id",
            "semester_id",
            name="uq_schedule_plan_speciality_subject_semester",
        ),
        Index("idx_schedule_plan_speciality", "speciality_id"),
        Index("idx_schedule_plan_semester", "semester_id"),
        Index("idx_schedule_plan_subject", "subject_id"),
        Index("idx_schedule_plan_year", "year"),
        # search plan fro speciality+semester
        Index("idx_schedule_plan_speciality_semester", "speciality_id", "semester_id"),
    )


class ScheduleItem(
    Base, UUIDPKMixin, TimestampMixin, CreatedByMixin, UpdateAtMixin, UpdatedByMixin
):
    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subject_id: Mapped[UUID] = mapped_column(
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    teacher_id: Mapped[UUID] = mapped_column(
        ForeignKey("teachers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    room_id: Mapped[UUID] = mapped_column(
        ForeignKey("rooms.id", ondelete="RESTRICT"),
        nullable=False,
    )
    semester_id: Mapped[UUID] = mapped_column(
        ForeignKey("semesters.id", ondelete="RESTRICT"),
        nullable=False,
    )
    time_slot_id: Mapped[UUID] = mapped_column(
        ForeignKey("time_slots.id", ondelete="RESTRICT"),
        nullable=False,
    )

    class_date: Mapped[Date] = mapped_column(Date, nullable=False)
    activity_type: Mapped[ActivityType] = mapped_column(
        ENUM(ActivityType, name="activity_type", create_type=True),
        default=ActivityType.lecture,
        nullable=False,
    )

    # rel
    group: Mapped["Group"] = relationship(
        "Group", back_populates="schedule_items", lazy="selectin"
    )

    subject: Mapped["Subject"] = relationship(
        "Subject", back_populates="schedule_items", lazy="selectin"
    )

    teacher: Mapped["Teacher"] = relationship(
        "Teacher", back_populates="schedule_items", lazy="selectin"
    )

    room: Mapped["Room"] = relationship(
        "Room", back_populates="schedule_items", lazy="selectin"
    )

    semester: Mapped["Semester"] = relationship(
        "Semester", back_populates="schedule_items", lazy="selectin"
    )

    time_slot: Mapped["TimeSlot"] = relationship(
        "TimeSlot", back_populates="schedule_items", lazy="selectin"
    )

    substitution: Mapped["TeacherSubstitution | None"] = relationship(
        "TeacherSubstitution",
        back_populates="schedule_item",
        uselist=False,
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "group_id", "class_date", "time_slot_id", name="uq_schedule_group_date_time"
        ),
        UniqueConstraint(
            "teacher_id",
            "class_date",
            "time_slot_id",
            name="uq_schedule_teacher_date_time",
        ),
        UniqueConstraint(
            "room_id", "class_date", "time_slot_id", name="uq_schedule_room_date_time"
        ),
        # search by class date
        Index("idx_schedule_item_class_date", "class_date"),
        # search by prof+date (schedule for prof)
        Index("idx_schedule_item_teacher_date", "teacher_id", "class_date"),
        # search by group+date (schedule for group)
        Index("idx_schedule_item_group_date", "group_id", "class_date"),
        # search by class+date
        Index("idx_schedule_item_room_date", "room_id", "class_date"),
        # search by semester
        Index("idx_schedule_item_semester", "semester_id"),
        # search by activity
        Index("idx_schedule_item_activity_type", "activity_type"),
    )
