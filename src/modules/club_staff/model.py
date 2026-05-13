from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.configurations.database import Base, int_pk


class ClubStaff(Base):
    __tablename__ = "club_staff"

    id: Mapped[int_pk]

    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True)
    club: Mapped["Club"] = relationship("Club", back_populates="staff_members")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="managed_clubs")

    staff_role: Mapped[str] = mapped_column(String(50), default="admin")


