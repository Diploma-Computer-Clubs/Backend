from datetime import datetime

from sqlalchemy import select, and_, func, update as sqlalchemy_update
from sqlalchemy.orm import joinedload

from src.shared.configurations.database import async_session_maker
from src.shared.dao.base import BaseDAO
from src.modules.bookings.model import Booking

class BookingDAO(BaseDAO):
    model = Booking

    @classmethod
    async def find_one_or_none_collision(cls, computer_id: int, start_time: datetime, end_time: datetime):
        async with async_session_maker() as session:
            query = select(cls.model).filter(
                cls.model.computer_id == computer_id,
                cls.model.is_active == True,
                and_(cls.model.start_time < end_time, cls.model.end_time > start_time)
            )
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def get_active_user_booking(cls, user_id: int):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(joinedload(cls.model.club), joinedload(cls.model.zone), joinedload(cls.model.computer))
                .filter(
                    cls.model.user_id == user_id,
                    cls.model.end_time > datetime.now(),
                    cls.model.is_active == True,
                )
                .order_by(cls.model.start_time.asc())
            )
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_related_bookings(cls, user_id: int, start_time: datetime, end_time: datetime):
        async with async_session_maker() as session:
            query = select(cls.model).filter(
                cls.model.user_id == user_id,
                cls.model.start_time == start_time,
                cls.model.end_time == end_time,
            )
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def update_check_in_status(cls, booking_id: int, is_checked_in: bool):
        return await cls.update(filter_by={"id": booking_id}, is_checked_in=is_checked_in, updated_at=func.now())

    @classmethod
    async def update_check_in_related(cls, user_id: int, start_time: datetime, end_time: datetime, is_checked_in: bool):
        async with async_session_maker() as session:
            async with session.begin():
                query = (
                    sqlalchemy_update(cls.model)
                    .filter(
                        cls.model.user_id == user_id,
                        cls.model.start_time == start_time,
                        cls.model.end_time == end_time,
                    )
                    .values(is_checked_in=is_checked_in, updated_at=func.now())
                )
                result = await session.execute(query)
                return result.rowcount

    @classmethod
    async def deactivate_related(cls, user_id: int, start_time: datetime, end_time: datetime):
        async with async_session_maker() as session:
            async with session.begin():
                query = (
                    sqlalchemy_update(cls.model)
                    .filter(
                        cls.model.user_id == user_id,
                        cls.model.start_time == start_time,
                        cls.model.end_time == end_time,
                        cls.model.is_active == True,
                    )
                    .values(is_active=False, updated_at=func.now())
                )
                result = await session.execute(query)
                return result.rowcount
