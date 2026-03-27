from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException

from src.modules.bookings.dao import BookingDAO
from src.modules.bookings.schemas import SBookingCreate
from src.modules.computers.dao import ComputerDAO


class BookingService:

    @classmethod
    async def create_booking(cls, bookings_info: List[SBookingCreate], user_id: int):
        existing_bookings = await BookingDAO.get_active_user_booking(user_id)
        if existing_bookings:
            raise HTTPException(
                status_code=400,
                detail="You already have an active user booking",
            )

        now = datetime.now()
        prepared_bookings = []

        for info in bookings_info:
            if info.start_time < now + timedelta(minutes=30):
                raise HTTPException(
                    status_code=400,
                    detail="Booking have to be 30 minutes ahead",
                )

            duration = info.end_time - info.start_time
            if duration > timedelta(hours=12):
                raise HTTPException(
                    status_code=400,
                    detail="Maximum booking duration is 12 hours",
                )

            if info.end_time > now + timedelta(hours=36):
                raise HTTPException(
                    status_code=400,
                    detail="Booking have to be less then 36 hours ahead",
                )

            computer = await ComputerDAO.find_computer_in_club(
                computer_id=info.computer_id,
                zone_id=info.zone_id,
                club_id=info.club_id
            )
            if not computer:
                raise HTTPException(status_code=404, detail="Computer not found")

            is_occupied = await BookingDAO.find_one_or_none_collision(
                computer_id=info.computer_id,
                start_time=info.start_time,
                end_time=info.end_time
            )
            if is_occupied:
                raise HTTPException(status_code=409, detail="Time is occupied")

            data = info.model_dump()
            data["user_id"] = user_id
            data["start_time"] = data["start_time"].replace(tzinfo=None)
            data["end_time"] = data["end_time"].replace(tzinfo=None)
            prepared_bookings.append(data)

        return await BookingDAO.add_list(prepared_bookings)

    @classmethod
    async def get_user_booking(cls, user_id: int):
        return await BookingDAO.get_active_user_booking(user_id)

    @classmethod
    async def delete_booking(cls, booking_id: int, user_id: int):
        booking = await BookingDAO.find_one_or_none(id=booking_id)

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )
        if booking.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this booking"
            )

        return await BookingDAO.delete(id=booking_id)