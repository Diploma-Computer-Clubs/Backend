from sqlalchemy.orm import Mapped

from src.shared.configurations.database import Base, int_pk, str_uniq


class Image(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    path: Mapped[str]