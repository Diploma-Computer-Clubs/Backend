import random

from sqlalchemy import func
from src.modules.users.dao import UserDAO
from src.modules.users.model import User
from src.modules.users.schemas import SUser, SUserPostData
from src.shared.redis.utils import get_code, delete_code, set_code
from src.shared.utils.auth_utils import get_password_hash
from src.shared.utils.sms_sender import send_sms_via_twilio


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
    async def reset_password_by_id(cls, user_id: int, new_password: str):
        hashed_password = get_password_hash(new_password)

        result = await UserDAO.update(filter_by={"id": user_id}, password=hashed_password, updated_at=func.now())
        return result > 0

    @classmethod
    async def find_user_by_phone_number(cls, phone_number: str) -> SUser | None:
        result = await UserDAO.find_one_or_none(phone_number=phone_number)
        if not result:
            return None
        return result

    @classmethod
    async def change_user_data(cls,  user: int, user_data: SUserPostData):
        result = await UserDAO.update(filter_by={"id": user},  city_id=user_data.city_id, full_name=user_data.full_name, updated_at=func.now())
        if not result:
            return None
        return {'message': 'Info changed successfully'}

    @classmethod
    async def delete_user(cls, user_id: int):
        return await UserDAO.delete(id=user_id)

    @classmethod
    async def request_verification(cls, phone: str):
        code = str(random.randint(100000, 999999))
        await set_code(phone, code)
        print(code)
        sent = await send_sms_via_twilio(phone, f"Code: {code}")
        return sent

    @classmethod
    async def verify_phone_code(cls, phone: str, code: str):
        saved_code = await get_code(phone)
        if not saved_code or saved_code != code:
            return False

        await delete_code(phone)
        return True