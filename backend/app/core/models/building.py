from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Integer,
    UniqueConstraint,
    UUID,
    ForeignKey,
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
from ...enums import RoomType

if TYPE_CHECKING:
    from . import ScheduleItem


class Building(
    Base, UUIDPKMixin, TimestampMixin, CreatedByMixin, UpdateAtMixin, UpdatedByMixin
):
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(150), nullable=False)

    # rel
    rooms: Mapped[list["Room"]] = relationship(
        "Room", back_populates="building", cascade="all,delete-orphan", lazy="selectin"
    )

    __table_args__ = (Index("idx_building_name", "name"),)


class Room(
    Base, UUIDPKMixin, TimestampMixin, CreatedByMixin, UpdateAtMixin, UpdatedByMixin
):
    room_number: Mapped[str] = mapped_column(String(10), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    room_type: Mapped[RoomType] = mapped_column(
        ENUM(RoomType, name="room_type", create_type=True),
        default=RoomType.common_class,
    )
    building_id: Mapped[UUID] = mapped_column(
        ForeignKey("buildings.id"), nullable=False
    )

    # rel
    building: Mapped[list["Building"]] = relationship(
        "Building",
        back_populates="rooms",
        lazy="selectin",
    )
    schedule_items: Mapped[list["ScheduleItem"]] = relationship(
        "ScheduleItem",
        back_populates="room",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("building_id", "room_number", name="unique_room_per_building"),
        CheckConstraint("capacity > 0", name="capacity_check"),
        Index("idx_room_building", "building_id"),
        Index("idx_room_type", "room_type"),
        Index("idx_room_capacity", "capacity"),
    )
