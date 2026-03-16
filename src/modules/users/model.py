from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.shared.configurations.database import Base, str_uniq, int_pk, str_password
from src.modules.cities.model import City
from enum import Enum

class Role(str, Enum):
    user = "user"
    admin = "admin"

class User(Base):
    id: Mapped[int_pk]
    phone_number: Mapped[str_uniq]
    password_hash: Mapped[str_password]
    full_name: Mapped[str]
    role: Mapped[Role] = mapped_column(default=Role.user, server_default=text("'user'"), nullable=False)
    reputation: Mapped[int] = mapped_column(server_default=text('100'))

    city_id: Mapped[int] = mapped_column(ForeignKey('cities.id'), nullable=False)
    city: Mapped["City"] = relationship("City", back_populates="users")

    clubs: Mapped[list["Club"]] = relationship("Club", back_populates="users")

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "full_name": self.full_name,
            "reputation": self.reputation,
            "password": self.password_hash,
            "city_id": self.city_id,
            "role": self.role,

        }
