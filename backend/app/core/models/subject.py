from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .helpers import Base
from .mixins import (
    UUIDPKMixin,
    CreatedByMixin,
    TimestampMixin,
    UpdateAtMixin,
    UpdatedByMixin,
)

if TYPE_CHECKING:
    from . import TeacherSubject
    from . import ScheduleItem
    from . import SchedulePlan
    from . import Teacher


class Subject(
    Base, UUIDPKMixin, TimestampMixin, CreatedByMixin, UpdateAtMixin, UpdatedByMixin
):
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)

    # rel
    teacher_subjects: Mapped[list["TeacherSubject"]] = relationship(
        "TeacherSubject",
        back_populates="subject",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    schedule_items: Mapped[list["ScheduleItem"]] = relationship(
        "ScheduleItem", back_populates="subject", lazy="selectin"
    )

    schedule_plans: Mapped[list["SchedulePlan"]] = relationship(
        "SchedulePlan", back_populates="subject", lazy="selectin"
    )

    @property
    def teachers(self) -> list["Teacher"]:
        # return the list of teachers who teach the subject
        return [ts.teacher for ts in self.teacher_subjects]
