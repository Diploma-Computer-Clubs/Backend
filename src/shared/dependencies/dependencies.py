from fastapi import Depends, HTTPException
from starlette import status
from src.modules.club_staff.service import ClubStaffService
from src.modules.clubs.service import ClubService
from src.shared.dependencies.user_dependency import get_current_user_id
from src.modules.users.dao import UserDAO
from src.modules.users.model import User


async def get_current_user(user_id: int = Depends(get_current_user_id)) -> User:
    user = await UserDAO.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')

    user.club_ids = []
    user.staff_role = None
    user.owner = "None"

    owned_clubs = await ClubService.get_club_by_owner_id(user.id)

    if owned_clubs:
        user.club_ids = [club.id for club in owned_clubs]
        user.owner = "Owner"
    else:
        staff_record = await ClubStaffService.get_membership_by_user_id(user.id)
        if staff_record:
            if isinstance(staff_record, list) and len(staff_record) > 0:
                user.club_ids = [staff_record[0].club_id]
                user.staff_role = staff_record[0].staff_role
            elif not isinstance(staff_record, list):
                user.club_ids = [staff_record.club_id]
                user.staff_role = staff_record.staff_role

    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, club_id: int, user: User = Depends(get_current_user)):
        club = await ClubService.get_club_by_id(club_id)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")

        if club.owner_id == user.id:
            return {"role": "owner", "club_id": club_id}

        staff_member = await ClubStaffService.get_member_by_club(user_id=user.id, club_id=club_id)

        if staff_member and staff_member.staff_role in self.allowed_roles:
            return {"role": staff_member.staff_role, "club_id": club_id}

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Access denied. This action is for club owners or specific staff only.")


async def super_admin_only(user: User = Depends(get_current_user)):
    if getattr(user, "role", None) != "admin":
        raise HTTPException(status_code=403,detail="This action is only for Global System Administrators")
    return user

