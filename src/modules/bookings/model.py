from datetime import datetime
from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.shared.configurations.database import Base, int_pk
from enum import Enum

class Status(str, Enum):
    free= "free",
    booked= "booked",
    not_available= "not available",

class Booking(Base):
    id: Mapped[int_pk]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    status: Mapped[Status] = mapped_column(default=Status.free, server_default=text("'free'"), nullable=False)
    total_price: Mapped[int]

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="bookings")

    computer_id: Mapped[int] = mapped_column(ForeignKey('computers.id'), nullable=False)
    computer: Mapped["Computer"] = relationship("Computer", back_populates="bookings")

    def to_dict(self):
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "total_price": self.total_price,
            "user_id": self.user_id,
            "computer_id": self.computer_id,
        }