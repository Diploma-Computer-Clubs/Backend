from sqlalchemy.orm import Mapped, relationship
from src.shared.configurations.database import Base, int_pk, str_uniq

class City(Base):
    __tablename__ = "cities"
    id: Mapped[int_pk]
    city: Mapped[str_uniq]

    users: Mapped[list["User"]] = relationship("User", back_populates="city")

    clubs: Mapped[list["Club"]] = relationship("Club", back_populates="city")