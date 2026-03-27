from datetime import time
from sqlalchemy import ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.configurations.database import Base, int_pk

class ZonePackage(Base):

    id: Mapped[int_pk]
    name: Mapped[str]
    start_time: Mapped[time] = mapped_column(Time, nullable=True)
    end_time: Mapped[time] = mapped_column(Time, nullable=True)
    duration: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    is_package: Mapped[bool] = mapped_column(default=False)

    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id", ondelete="CASCADE"))
    zone: Mapped["Zone"] = relationship("Zone", back_populates="packages")
