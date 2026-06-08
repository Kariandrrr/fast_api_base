from sqlalchemy import (
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from .helpers import Base
from .mixins import UUIDPKMixin


class Subject(Base, UUIDPKMixin):
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)

    # TODO: rel
