from typing import List

from fastapi import APIRouter, Depends

from src.modules.bookings.schemas import SBookingCreate, SBookingView
from src.modules.bookings.service import BookingService
from src.shared.dependencies.user_dependency import get_current_user_id

router = APIRouter(prefix="/bookings", tags=["Work with bookings"])


@router.post('/create_booking', summary='Create booking')
async def create_booking(booking_info: List[SBookingCreate], user_id: int = Depends(get_current_user_id)):
    return await BookingService.create_booking(booking_info, user_id)


@router.get('/get_bookings', summary='Get booking', response_model=List[SBookingView])
async def get_bookings(user_id: int = Depends(get_current_user_id)):
    return await BookingService.get_user_booking(user_id)


@router.delete('/delete_booking', summary='Delete booking')
async def delete_booking(booking_id: int, user_id: int = Depends(get_current_user_id)):
    return await BookingService.delete_booking(booking_id, user_id)