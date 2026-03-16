from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.shared.configurations.database import Base, int_pk

class Zone(Base):
    id: Mapped[int_pk]
    name: Mapped[str]
    cost: Mapped[int]

    club_id: Mapped[int] = mapped_column(ForeignKey('clubs.id'), nullable=False)
    club: Mapped["Club"] = relationship("Club", back_populates="zones")

    computers: Mapped[list["Computer"]] = relationship("Computer", back_populates="zone")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cost": self.cost,
            "club_id": self.club_id,
        }