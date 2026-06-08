from datetime import date

from sqlalchemy import (
    Integer,
    UUID,
    ForeignKey,
    Date,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from .helpers import Base
from .mixins import UUIDPKMixin
from ...enums import PracticeType


class Practice(Base, UUIDPKMixin):
    semester_id: Mapped[UUID] = mapped_column(
        ForeignKey("semesters.id", ondelete="RESTRICT"), nullable=False
    )

    type: Mapped[PracticeType] = mapped_column(
        ENUM(PracticeType, name="practice_type", create_type=True),
        default=PracticeType.educational,
        nullable=False,
    )

    practice_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    practice_end_date: Mapped[date] = mapped_column(Date, nullable=False)

    hours: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "practice_start_time < practice_end_time", name="ck_practice_time_order"
        ),
        CheckConstraint("hours > 0 AND hours <= 1000", name="ck_practice_hours_range"),
    )

    # TODO: rel
