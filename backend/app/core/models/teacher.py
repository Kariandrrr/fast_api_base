from datetime import time, date
from uuid import UUID

from sqlalchemy import (
    Time,
    CheckConstraint,
    Date,
    UniqueConstraint,
    String,
    ForeignKey,
    Boolean,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from .helpers import Base
from .mixins import UUIDPKMixin
from ...enums import DayOfWeek


class Teacher(Base, UUIDPKMixin):
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(30), nullable=True)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)

    is_full_time: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_invited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    hired_date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "NOT (is_full_time = TRUE AND is_invited = TRUE)",
            name="check_teacher_status",
        ),
    )
    # TODO: rel


class TeacherAvailability(Base, UUIDPKMixin):
    __tablename__ = "teacher_availability"

    teacher_id: Mapped[UUID] = mapped_column(ForeignKey("teachers.id"), nullable=False)

    day_of_week: Mapped[DayOfWeek] = mapped_column(
        ENUM(DayOfWeek, name="day_of_week", create_type=True), nullable=False
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "end_time > start_time", name="check_time_order_in_availability"
        ),
        UniqueConstraint(
            "teacher_id", "day_of_week", "start_time", name="uq_teacher_day_time"
        ),
    )
    # TODO: rel


# TODO: teacher substitution
