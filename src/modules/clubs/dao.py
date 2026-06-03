from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload

from src.modules.bookings.model import Booking
from src.modules.computers.model import Computer
from src.modules.zones.model import Zone
from src.shared.configurations.database import async_session_maker
from src.shared.dao.base import BaseDAO
from src.modules.clubs.model import Club

class ClubDAO(BaseDAO):
    model = Club

    @classmethod
    async def get_club_with_zones(cls, club_id: int):
        return await cls.find_one_or_none(joinedload(cls.model.zones), id=club_id)

    @classmethod
    async def get_clubs(cls, user_id: int):
        return await cls.find_all_unique(joinedload(cls.model.zones), owner_id=user_id)

    @classmethod
    async def find_full_data(cls, city_id: int):
        return await cls.find_all(
            joinedload(cls.model.city),
            selectinload(cls.model.zones),
            city_id=city_id
        )

    @classmethod
    async def get_min_price_by_club(cls, club_id: int):
        async with async_session_maker() as session:
            query = (
                select(func.min(Zone.cost))
                .select_from(cls.model)
                .join(Zone, cls.model.id == Zone.club_id)
                .where(cls.model.id == club_id)
            )
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def get_zones_with_computers_status(cls, club_id: int, start_time: datetime, end_time: datetime):
        start_time = start_time.replace(tzinfo=None)
        end_time = end_time.replace(tzinfo=None)

        async with async_session_maker() as session:
            query = (
                select(Zone)
                .filter_by(club_id=club_id)
                .options(
                    selectinload(Zone.computers)
                    .                    selectinload(Computer.bookings.and_(
                        Booking.is_active == True,
                        Booking.start_time < end_time,
                        Booking.end_time > start_time
                    )).joinedload(Booking.user)
                )
            )
            result = await session.execute(query)
            return result.unique().scalars().all()

    @classmethod
    async def get_club_statistics_data(cls, club_id: int, start_time: datetime, end_time: datetime):
        start_time = start_time.replace(tzinfo=None)
        end_time = end_time.replace(tzinfo=None)

        async with async_session_maker() as session:
            query = (
                select(Zone)
                .filter_by(club_id=club_id)
                .options(
                    selectinload(Zone.packages),
                    selectinload(Zone.computers)
                    .selectinload(Computer.bookings.and_(
                        Booking.is_checked_in == True,
                        Booking.end_time <= datetime.now(),
                        Booking.start_time < end_time,
                        Booking.end_time > start_time
                    ))
                )
            )
            result = await session.execute(query)
            return result.unique().scalars().all()

    @classmethod
    async def get_club_with_owner(cls, club_id: int):
        return await cls.find_one_or_none(joinedload(cls.model.owner), id=club_id)
