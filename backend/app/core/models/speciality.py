from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .helpers import Base
from .mixins import UUIDPKMixin

if TYPE_CHECKING:
    from . import Group
    from . import SchedulePlan


class Speciality(Base, UUIDPKMixin):
    __tablename__ = "specialities"

    name: Mapped[str] = mapped_column(String(40), nullable=False)
    code: Mapped[str] = mapped_column(String(15), nullable=False)

    # rel
    groups: Mapped[list["Group"]] = relationship(
        "Group",
        back_populates="speciality",
        lazy="selectin",
    )

    schedule_plans: Mapped[list["SchedulePlan"]] = relationship(
        "SchedulePlan",
        back_populates="speciality",
        lazy="selectin",
    )

    __table_args__ = (UniqueConstraint("name", "code", name="uq_speciality_name_code"),)
