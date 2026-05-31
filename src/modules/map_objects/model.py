from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.shared.configurations.database import Base, int_pk


class MapObject(Base):
    __tablename__ = "map_objects"

    id: Mapped[int_pk]
    type: Mapped[str]
    label: Mapped[str]
    x: Mapped[float]
    y: Mapped[float]
    width: Mapped[float]
    height: Mapped[float]
    rotation: Mapped[float]

    club_id: Mapped[int] = mapped_column(ForeignKey('clubs.id', ondelete="CASCADE"))
    club: Mapped["Club"] = relationship("Club", back_populates="map_objects")
