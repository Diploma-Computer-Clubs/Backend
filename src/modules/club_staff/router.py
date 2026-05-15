from fastapi import APIRouter, Depends, HTTPException

from src.modules.club_staff.service import ClubStaffService
from src.modules.club_staff.shemas import SClubStaffAdd
from src.modules.clubs.service import ClubService
from src.modules.users.service import UserService
from src.shared.dependencies.dependencies import RoleChecker

router = APIRouter(prefix="/clubs", tags=['Club Staff Management'], dependencies=[Depends(RoleChecker([]))])


@router.post("/{club_id}/staff", summary="Add staff member (owner)")
async def add_staff(club_id: int, staff_data: SClubStaffAdd):
    user = await UserService.find_user_by_phone_number(staff_data.phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    owned_clubs = await ClubService.get_club_by_owner_id(user.id)
    if owned_clubs:
        raise HTTPException(status_code=409, detail="User already owner of club(s)")
    return await ClubStaffService.add_staff_member(club_id, user.id, staff_data.staff_role)


@router.get("/{club_id}/staff", summary="Get staff list (owner)")
async def list_staff(club_id: int):
    return await ClubStaffService.get_staff_list(club_id)

@router.delete("/{club_id}/staff", summary="Delete staff (owner)")
async def delete_staff(club_id: int, staff_id: int,):
    return await ClubStaffService.delete_staff(club_id, staff_id)