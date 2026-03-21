from typing import List

from fastapi import HTTPException

from src.modules.bookings.dao import BookingDAO
from src.modules.bookings.schemas import SBookingCreate
from src.modules.computers.dao import ComputerDAO
from src.shared.configurations.database import async_session_maker


class BookingService:

    @classmethod
    async def create_booking(cls, bookings_info: List[SBookingCreate]):
        prepared_bookings = []

        for info in bookings_info:
            computer = await ComputerDAO.find_computer_in_club(
                computer_id=info.computer_id,
                zone_id=info.zone_id,
                club_id=info.club_id
            )

            if not computer:
                raise HTTPException(
                    status_code=404,
                    detail=f"Computer {info.computer_id} not found in this zone/club",
                )

            is_occupied = await BookingDAO.find_one_or_none_collision(
                computer_id=info.computer_id,
                start_time=info.start_time,
                end_time=info.end_time
            )

            if is_occupied:
                raise HTTPException(
                    status_code=409,
                    detail=f"Computer {info.computer_id} already booked for this time"
                )

            data = info.model_dump()
            data["start_time"] = data["start_time"].replace(tzinfo=None)
            data["end_time"] = data["end_time"].replace(tzinfo=None)
            prepared_bookings.append(data)

        return await BookingDAO.add_list(prepared_bookings)

    @classmethod
    async def get_user_bookings(cls, user_id: int):
        return await BookingDAO.get_active_user_bookings(user_id)
