from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Integer,
    UUID,
    ForeignKey,
    Date,
    CheckConstraint,
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
from ...enums import PracticeType

if TYPE_CHECKING:
    from . import Semester


class Practice(
    Base, UUIDPKMixin, TimestampMixin, CreatedByMixin, UpdateAtMixin, UpdatedByMixin
):
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

    # rel
    semester: Mapped["Semester"] = relationship(
        "Semester", back_populates="practices", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint(
            "practice_start_date < practice_end_date", name="ck_practice_date_order"
        ),
        CheckConstraint("hours > 0 AND hours <= 1000", name="ck_practice_hours_range"),
        Index("idx_practice_semester", "semester_id"),
        Index("idx_practice_type", "type"),
        Index("idx_practice_dates", "practice_start_date", "practice_end_date"),
    )
