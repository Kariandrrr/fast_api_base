from uuid import UUID

from sqlalchemy import (
    String,
    UniqueConstraint,
    ForeignKey,
    Integer,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from .helpers import Base
from .mixins import UUIDPKMixin
from ...enums import Shift


class Group(Base, UUIDPKMixin):
    speciality_id: Mapped[UUID] = mapped_column(
        ForeignKey("specialities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    shift: Mapped[Shift] = mapped_column(
        ENUM(Shift, name="shift_type", create_type=True), default=Shift.first
    )
    student_count: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "student_count BETWEEN 1 AND 35",
            name="ck_group_student_count_range",
        ),
        CheckConstraint("year BETWEEN 1 AND 7", name="ck_group_year_range"),
        UniqueConstraint(
            "speciality_id", "name", "year", name="uq_group_speciality_name_year"
        ),
    )
    # TODO: rel
