from datetime import datetime, timedelta
from typing import List
from fastapi import HTTPException, status

from src.modules.bookings.dao import BookingDAO
from src.modules.bookings.schemas import SBookingCreate, SBookingCheckIn
from src.modules.bookings.tasks import deactivate_booking_if_no_show, restore_reputation_task
from src.modules.computers.dao import ComputerDAO
from src.modules.users.service import UserService


class BookingService:

    @classmethod
    async def _check_reputation_rules(cls, bookings_info: List[SBookingCreate], user_id: int):
        reputation = await UserService.get_user_reputation(user_id)
        now = datetime.now()

        if reputation <= 69:
            raise HTTPException(status_code=400, detail="Booking is unavailable due to low reputation")

        if len(bookings_info) > 5:
            raise HTTPException(status_code=400, detail="You can book only 5 computers")

        if reputation <= 89 and len(bookings_info) > 1:
            raise HTTPException(status_code=400, detail="You can book only 1 computer")

        if reputation <= 79:
            for info in bookings_info:
                if info.start_time > now + timedelta(hours=2):
                    raise HTTPException(status_code=400, detail="Booking can be no more than 2 hours ahead")

                if (info.end_time - info.start_time) > timedelta(hours=5):
                    raise HTTPException(status_code=400, detail="Max duration is 5 hours for your reputation")

    @classmethod
    async def _prepare_and_validate_bookings(cls, bookings_info: List[SBookingCreate], user_id: int) -> List[dict]:
        now = datetime.now()
        prepared_bookings = []

        for info in bookings_info:
            if info.start_time < now + timedelta(minutes=30):
                raise HTTPException(status_code=400, detail="Booking must be at least 30 min ahead")

            if (info.end_time - info.start_time) > timedelta(hours=12):
                raise HTTPException(status_code=400, detail="Max duration is 12 hours")

            computer = await ComputerDAO.find_computer_in_club(
                computer_id=info.computer_id,
                zone_id=info.zone_id,
                club_id=info.club_id
            )
            if not computer:
                raise HTTPException(status_code=404, detail="Computer not found in this zone/club")

            is_occupied = await BookingDAO.find_one_or_none_collision(
                computer_id=info.computer_id,
                start_time=info.start_time,
                end_time=info.end_time
            )
            if is_occupied:
                raise HTTPException(status_code=409, detail="This time slot is already occupied")

            data = info.model_dump()
            data.update({
                "user_id": user_id,
                "start_time": info.start_time.replace(tzinfo=None),
                "end_time": info.end_time.replace(tzinfo=None)
            })
            prepared_bookings.append(data)

        return prepared_bookings

    @classmethod
    def _schedule_booking_tasks(cls, bookings):
        groups = {}
        for booking in bookings:
            key = (booking.user_id, booking.start_time, booking.end_time)
            if key not in groups:
                groups[key] = booking

        for booking in groups.values():
            eta = booking.start_time + timedelta(hours=1)
            countdown = max(0, int((eta - datetime.now()).total_seconds()))
            deactivate_booking_if_no_show.apply_async(args=[booking.id], countdown=countdown)

    @classmethod
    def _schedule_reputation_restore(cls, user_id: int):
        week_seconds = 7 * 24 * 3600
        for week in range(1, 4):
            restore_reputation_task.apply_async(args=[user_id], countdown=week * week_seconds)

    @classmethod
    async def process_no_show(cls, booking_id: int):
        booking = await BookingDAO.find_one_or_none(id=booking_id)
        if not booking or not booking.is_active:
            return

        if booking.is_checked_in:
            return

        related = await BookingDAO.get_related_bookings(
            booking.user_id, booking.start_time, booking.end_time
        )
        if not any(b.is_active for b in related):
            return

        await BookingDAO.deactivate_related(booking.user_id, booking.start_time, booking.end_time)
        await UserService.deduct_reputation(booking.user_id, 10)
        cls._schedule_reputation_restore(booking.user_id)

    @classmethod
    async def create_booking(cls, bookings_info: List[SBookingCreate], user_id: int):
        await cls._check_reputation_rules(bookings_info, user_id)
        existing = await BookingDAO.get_active_user_booking(user_id)
        if existing:
            raise HTTPException(status_code=400, detail="You already have an active booking")

        prepared_bookings = await cls._prepare_and_validate_bookings(bookings_info, user_id)
        bookings = await BookingDAO.add_list(prepared_bookings)
        cls._schedule_booking_tasks(bookings)
        return bookings

    @classmethod
    async def create_admin_booking(cls, bookings_info: List[SBookingCreate], user_id: int):
        prepared_bookings = await cls._prepare_and_validate_bookings(bookings_info, user_id)
        bookings = await BookingDAO.add_list(prepared_bookings)
        cls._schedule_booking_tasks(bookings)
        return bookings

    @classmethod
    async def get_user_booking(cls, user_id: int):
        return await BookingDAO.get_active_user_booking(user_id)

    @classmethod
    async def delete_booking(cls, booking_id: int, user_id: int):
        booking = await BookingDAO.find_one_or_none(id=booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        if booking.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not allowed to delete others' bookings")

        now = datetime.now()
        if booking.start_time < now + timedelta(minutes=30):
            raise HTTPException(status_code=400, detail="Booking cannot be deleted less than 30 minutes before start")

        return await BookingDAO.delete(id=booking_id)

    @classmethod
    async def delete_booking_admin(cls, booking_id: int):
        booking = await BookingDAO.find_one_or_none(id=booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return await BookingDAO.delete(id=booking_id)

    @classmethod
    async def update_check_in_status(cls, booking_info: SBookingCheckIn):
        booking = await BookingDAO.find_one_or_none(id=booking_info.booking_id)
        if not booking:
            return False

        result = await BookingDAO.update_check_in_related(
            booking.user_id,
            booking.start_time,
            booking.end_time,
            booking_info.is_checked_in,
        )
        return result > 0
