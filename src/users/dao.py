from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.configurations.database import async_session_maker
from src.dao.base import BaseDAO
from src.users.users import User

class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def find_full_data(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).options(joinedload(cls.model.city)).filter_by(id=user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()