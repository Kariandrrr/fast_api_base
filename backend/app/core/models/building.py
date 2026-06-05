from sqlalchemy import (
    String,
    Integer,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from ...enums.room_type_enum import RoomType


class Building(Base):
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(150), nullable=False)


class Room(Base):
    room_number: Mapped[str] = mapped_column(String(10), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    room_type: Mapped[RoomType] = mapped_column(ENUM(RoomType, name="room_type",),
                                                default=RoomType.common_class)
    #TODO: relation with building (id)
    #TODO: add to enum gym