from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.shared.configurations.database import Base, int_pk, str_uniq, float_bull_true


class Club(Base):
    id: Mapped[int_pk]
    name: Mapped[str]
    address: Mapped[str_uniq]
    image_url: Mapped[str]
    promos: Mapped[dict | list] = mapped_column(JSONB, nullable=True, default={})
    description: Mapped[str]
    rating: Mapped[float]
    latitude: Mapped[float_bull_true]
    longitude: Mapped[float_bull_true]

    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="clubs")

    city_id: Mapped[int] = mapped_column(ForeignKey('cities.id'), nullable=False)
    city: Mapped["City"] = relationship("City", back_populates="clubs")

    zones: Mapped[list["Zone"]] = relationship("Zone", back_populates="club")

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="club")
