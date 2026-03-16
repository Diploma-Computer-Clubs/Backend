from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.shared.configurations.database import Base, int_pk
from src.modules.cities.model import City
from src.modules.users.model import User

class Club(Base):
    id: Mapped[int_pk]
    name: Mapped[str]
    address: Mapped[str]
    image_url: Mapped[str]
    promos: Mapped[dict | list] = mapped_column(JSONB, nullable=True, default={})
    description: Mapped[str]
    rating: Mapped[float]

    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="clubs")

    city_id: Mapped[int] = mapped_column(ForeignKey('cities.id'), nullable=False)
    city: Mapped["City"] = relationship("City", back_populates="clubs")

    zones: Mapped[list["Zone"]] = relationship("Zone", back_populates="club")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "image_url": self.image_url,
            "description": self.description,
            "promos": self.promos,
            "rating": self.rating,
            "city_id": self.city_id,
            "owner_id": self.owner_id
        }