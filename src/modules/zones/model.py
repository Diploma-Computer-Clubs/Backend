from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.shared.configurations.database import Base, int_pk, str_null_true


class Zone(Base):
    id: Mapped[int_pk]
    name: Mapped[str]
    cost: Mapped[int]
    cpu: Mapped[str_null_true]
    gpu: Mapped[str_null_true]
    ram: Mapped[str_null_true]
    ssd: Mapped[str_null_true]
    monitor: Mapped[str_null_true]

    club_id: Mapped[int] = mapped_column(ForeignKey('clubs.id', ondelete="CASCADE"), nullable=True)
    club: Mapped["Club"] = relationship("Club", back_populates="zones")

    computers: Mapped[list["Computer"]] = relationship("Computer", back_populates="zone", cascade="all, delete-orphan", passive_deletes=True)

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="zone", cascade="all, delete-orphan", passive_deletes=True)

    packages: Mapped[list["ZonePackage"]] = relationship("ZonePackage", back_populates="zone", cascade="all, delete-orphan", passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cost": self.cost,
            "club_id": self.club_id,
        }