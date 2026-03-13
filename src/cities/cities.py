from sqlalchemy.orm import Mapped, relationship
from src.configurations.database import Base, int_pk, str_uniq

class City(Base):
    __tablename__ = "cities"
    id: Mapped[int_pk]
    city: Mapped[str_uniq]
    #Зеркальное подключение FK
    users: Mapped[list["User"]] = relationship("User", back_populates="city")