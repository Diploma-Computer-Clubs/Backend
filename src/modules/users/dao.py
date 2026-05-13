from sqlalchemy.orm import joinedload

from src.shared.dao.base import BaseDAO
from src.modules.users.model import User

class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def get_user_by_id(cls, user_id: int):
        return await UserDAO.find_one_or_none(joinedload(User.city), id=user_id)
