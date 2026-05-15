from fastapi import HTTPException

from src.modules.club_staff.dao import ClubStaffDAO
from src.modules.club_staff.shemas import SClubStaffAdd
from sqlalchemy.orm import joinedload
from src.modules.club_staff.model import ClubStaff


class ClubStaffService:
    @classmethod
    async def add_staff_member(cls, club_id: int, user_id: int, role: str):
        existing_staff = await ClubStaffDAO.find_one_or_none(user_id=user_id)

        if existing_staff:
            raise HTTPException(status_code=409,detail="This user is already a staff member")

        return await ClubStaffDAO.add(club_id=club_id, user_id=user_id, staff_role=role)

    @classmethod
    async def get_staff_list(cls, club_id: int):
        return await ClubStaffDAO.get_staff_by_club(club_id)

    @classmethod
    async def get_member_by_club(cls, user_id: int, club_id: int):
        return await ClubStaffDAO.find_one_or_none(user_id=user_id, club_id=club_id)

    @classmethod
    async def get_membership_by_user_id(cls, user_id: int):
        return await ClubStaffDAO.find_one_or_none(user_id=user_id)

    @classmethod
    async def delete_staff(cls, club_id: int, user_id: int):
        return await ClubStaffDAO.delete(club_id=club_id, user_id=user_id)
