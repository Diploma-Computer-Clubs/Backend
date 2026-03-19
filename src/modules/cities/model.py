from sqlalchemy.orm import Mapped, relationship, mapped_column
from src.shared.configurations.database import Base, int_pk, str_uniq

class City(Base):
    __tablename__ = "cities"
    id: Mapped[int_pk]
    city: Mapped[str_uniq]
    latitude: Mapped[float] = mapped_column(nullable=True)
    longitude: Mapped[float] = mapped_column(nullable=True)

    users: Mapped[list["User"]] = relationship("User", back_populates="city")

    clubs: Mapped[list["Club"]] = relationship("Club", back_populates="city")