from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.shared.configurations.database import Base, int_pk, bool_true

class Booking(Base):
    id: Mapped[int_pk]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    total_price: Mapped[int]
    is_checked_in: Mapped[Optional[bool]] = mapped_column(default=False, server_default=text('false'), nullable=True)
    is_active: Mapped[bool_true]

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="SET NULL"), nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="bookings")

    computer_id: Mapped[int] = mapped_column(ForeignKey('computers.id', ondelete="CASCADE"), nullable=True)
    computer: Mapped["Computer"] = relationship("Computer", back_populates="bookings")

    zone_id: Mapped[int] = mapped_column(ForeignKey('zones.id', ondelete="CASCADE"), nullable=True)
    zone: Mapped["Zone"] = relationship("Zone", back_populates="bookings")

    club_id: Mapped[int] = mapped_column(ForeignKey('clubs.id', ondelete="CASCADE"), nullable=True)
    club: Mapped["Club"] = relationship("Club", back_populates="bookings")
