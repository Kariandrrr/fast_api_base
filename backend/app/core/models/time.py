from datetime import time, date

from sqlalchemy import (
    Integer, Time, CheckConstraint, Date, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from .helpers import Base
from .mixins import UUIDPKMixin
from ...enums import SlotNumber


class TimeSlots(Base, UUIDPKMixin):
    slot_number: Mapped[SlotNumber] = mapped_column(
        ENUM(SlotNumber, name="slot_number", create_type=True) ,default=SlotNumber.one, nullable=False
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    __table_args__ = (
        CheckConstraint('end_time > start_time', name='check_time_order'),
        UniqueConstraint('slot_number', name='slot_number_unique'),
    )

    #TODO: relations


class Semester(Base, UUIDPKMixin):
    academic_year: Mapped[int] = mapped_column(Integer, nullable=False)
    semester_number: Mapped[int] = mapped_column(Integer, nullable=False)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    session_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    session_end_date: Mapped[date] = mapped_column(Date, nullable=False)

    practice_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    practice_end_date: Mapped[date] = mapped_column(Date, nullable=False)


    __table_args__ = (
        CheckConstraint(
            'academic_year BETWEEN 1 AND 7',
            name='check_academic_year_range'
            ),
        CheckConstraint(
            'semester_number BETWEEN 1 AND 14',
            name='check_semester_number_range'
        ),
        CheckConstraint(
            'end_date > start_date', name='check_semester_dates'
        ),
        CheckConstraint(
            'session_end_date > session_start_date', name='check_session_dates'
        ),
        CheckConstraint(
            'practice_end_date > practice_start_date', name='check_practice_dates'
        ),
        UniqueConstraint('academic_year', 'semester_number', name='unique_semester_year_number'),
    )
    # TODO: relations
