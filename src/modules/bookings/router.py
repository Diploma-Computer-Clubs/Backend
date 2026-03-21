from typing import List

from fastapi import APIRouter, Depends

from src.modules.bookings.model import Booking
from src.modules.bookings.schemas import SBookingCreate, SMyBookingView
from src.modules.bookings.service import BookingService
from src.shared.dependencies.user_dependency import get_current_user_id

router = APIRouter(prefix="/bookings", tags=["Work with bookings"])


@router.post('/create_booking', summary='Create booking')
async def create_booking(booking_info: List[SBookingCreate], user_id: int = Depends(get_current_user_id)):
    return await BookingService.create_booking(booking_info)

#
@router.get('/get_bookings', summary='Get bookings', response_model=List[SMyBookingView])
async def get_bookings(user_id: int = Depends(get_current_user_id)):
    return await BookingService.get_user_bookings(user_id)