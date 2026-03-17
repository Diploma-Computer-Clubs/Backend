from sqlalchemy import func
from src.modules.users.dao import UserDAO
from src.modules.users.schemas import SUser
from src.shared.utils.auth_utils import get_password_hash


class UserService:
    @classmethod
    async def register_new_user(cls, user_data: SUser):
        existing_user = await UserDAO.find_one_or_none(phone_number=user_data.phone_number)
        if existing_user:
            return None

        user_dict = user_data.model_dump()
        user_dict['password'] = get_password_hash(user_data.password)

        new_user = await UserDAO.add(**user_dict)
        return new_user

    @classmethod
    async def reset_password(cls, phone: str, new_password: str):
        hashed_password = get_password_hash(new_password)

        updated_count = await UserDAO.update(
            filter_by={"phone_number": phone},
            password=hashed_password,
            updated_at=func.now()
        )

        if updated_count == 0:
            return None

        return await UserDAO.find_one_or_none(phone_number=phone)

    @classmethod
    async def find_user_by_phone_number(cls, phone_number: str) -> SUser | None:
        result = await UserDAO.find_one_or_none(phone_number=phone_number)
        if not result:
            return None
        return result
