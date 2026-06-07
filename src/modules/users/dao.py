from typing import List

from sqlalchemy.orm import joinedload
from sqlalchemy import func

from src.modules.users.schemas import SUserGetData
from src.shared.dao.base import BaseDAO
from src.modules.users.model import User

class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def get_user_by_id(cls, user_id: int):
        return await UserDAO.find_one_or_none(joinedload(User.city), id=user_id)

    @classmethod
    async def get_users(cls, role: str):
        return await UserDAO.find_all(joinedload(User.city), role=role)

    @classmethod
    async def update_reputation(cls, user_id: int, reputation: int):
        return await cls.update(filter_by={"id": user_id}, reputation=reputation, updated_at=func.now())
