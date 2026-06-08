from sqlalchemy import (
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .helpers import Base
from .mixins import UUIDPKMixin


class Speciality(Base, UUIDPKMixin):
    __tablename__ = "specialities"

    name: Mapped[str] = mapped_column(String(40), nullable=False)
    code: Mapped[str] = mapped_column(String(15), nullable=False)

    __table_args__ = (UniqueConstraint("name", "code", name="uq_speciality_name_code"),)
    # TODO: rel
