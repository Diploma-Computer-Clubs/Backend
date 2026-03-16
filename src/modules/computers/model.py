from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.shared.configurations.database import Base, int_pk
from src.modules.zones.model import Zone

class Computer(Base):
    id: Mapped[int_pk]
    number: Mapped[int]
    specification: Mapped[str]
    is_Active: Mapped[bool]

    zone_id: Mapped[int] = mapped_column(ForeignKey('zones.id'), nullable=False)
    zone: Mapped["Zone"] = relationship("Zone", back_populates="computers")

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="computer")

    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "specification": self.specification,
            "is_Active": self.is_Active,
            "zone_id": self.zone_id,
        }