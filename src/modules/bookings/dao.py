from datetime import datetime

from sqlalchemy import select, and_
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
                and_(
                    cls.model.start_time < end_time,
                    cls.model.end_time > start_time
                )
            )
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def get_active_user_booking(cls, user_id: int):
        async with async_session_maker() as session:
            now = datetime.now()

            query = (
                select(cls.model)
                .options(
                    joinedload(cls.model.club),
                    joinedload(cls.model.zone),
                    joinedload(cls.model.computer)
                )
                .filter(
                    cls.model.user_id == user_id,
                    cls.model.end_time > now
                )
                .order_by(cls.model.start_time.asc())
            )

            result = await session.execute(query)
            return result.scalars().all()
