from sqlalchemy.orm import joinedload

from src.modules.club_staff.model import ClubStaff
from src.shared.dao.base import BaseDAO

class ClubStaffDAO(BaseDAO):
    model = ClubStaff

    @classmethod
    async def get_staff_by_club(cls, club_id: int):
        return await cls.find_all(joinedload(cls.model.user), club_id=club_id)
