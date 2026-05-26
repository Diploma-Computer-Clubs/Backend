from typing import List

from fastapi import APIRouter, Depends

from src.modules.bookings.schemas import SBookingCreate, SBookingView, SBookingCheckIn
from src.modules.bookings.service import BookingService
from src.shared.dependencies.dependencies import RoleChecker
from src.shared.dependencies.user_dependency import get_current_user_id

router = APIRouter(prefix="/bookings", tags=["Bookings Management"])

@router.post("", summary="Create new bookings")
async def create_booking(booking_info: List[SBookingCreate], user_id: int = Depends(get_current_user_id)):
    return await BookingService.create_booking(booking_info, user_id)

@router.post("/admin", summary="Create new bookings (admin, owner)")
async def create_booking(booking_info: List[SBookingCreate], user: int = Depends(RoleChecker(["admin"])), user_id: int = Depends(get_current_user_id)):
    return await BookingService.create_admin_booking(booking_info, user_id)

@router.get("/me", summary="Get my active bookings", response_model=List[SBookingView])
async def get_my_bookings(user_id: int = Depends(get_current_user_id)):
    return await BookingService.get_user_booking(user_id)

@router.delete("/{booking_id}", summary="Cancel booking")
async def delete_booking(booking_id: int, user_id: int = Depends(get_current_user_id)):
    return await BookingService.delete_booking(booking_id, user_id)

@router.delete("/{booking_id}/admin", summary="Cancel booking (admin, owner)")
async def delete_booking(booking_id: int, user_id: int = Depends(RoleChecker(["admin"]))):
    return await BookingService.delete_booking_admin(booking_id)

@router.patch("/check-in", summary="Change booking check-in status (admin, owner)")
async def update_check_in_status(booking_info: SBookingCheckIn, user_id: int = Depends(RoleChecker(["admin"]))):
    return await BookingService.update_check_in_status(booking_info)
