from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from src.shared.configurations.database import async_session_maker
from src.shared.dao.base import BaseDAO
from src.modules.clubs.model import Club

class ClubDAO(BaseDAO):
    model = Club

    @classmethod
    async def find_full_data(cls, city_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).options(joinedload(cls.model.city)).filter_by(city_id=city_id)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def count_by_city(cls, city_id: int):
        async with async_session_maker() as session:
            query = select(func.count(cls.model.id)).filter_by(city_id=city_id)
            result = await session.execute(query)
            return result.scalar()

