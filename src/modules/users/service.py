import logging
import random
from datetime import datetime
from typing import List

from sqlalchemy import func
from src.modules.users.dao import UserDAO
from src.modules.users.schemas import SUser, SUserPostData, SUserGetData
from src.shared.schemas.schemas import Role
from src.shared.redis.utils import get_code, delete_code, set_code
from src.shared.utils.auth_utils import get_password_hash
from src.shared.utils.sms_sender import send_sms_via_twilio

logger = logging.getLogger(__name__)

class UserService:
    @classmethod
    async def register_new_user(cls, user_data: SUser):
        existing_user = await UserDAO.find_one_or_none(phone_number=user_data.phone_number)
        if existing_user:
            return None
        user_dict = user_data.model_dump()
        user_dict['password'] = get_password_hash(user_data.password)
        return await UserDAO.add(**user_dict)

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
    async def find_all_users(cls) -> List[SUserGetData] | None:
        owner = "owner"
        result = await UserDAO.get_users(role=owner)
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
    async def change_user_role(cls, phone_number: str, from_role: Role, to_role: Role):
        user = await UserService.find_user_by_phone_number(phone_number)
        if not user:
            raise LookupError("User not found")

        current_role = getattr(getattr(user, "role", None), "value", getattr(user, "role", None))
        if current_role != from_role.value:
            raise ValueError(f'User role must be "{from_role.value}"')

        result = await UserDAO.update(filter_by={"phone_number": phone_number}, role=to_role, updated_at=func.now())
        return result > 0

    @classmethod
    async def request_verification(cls, phone: str) -> bool:
        code = str(random.randint(100000, 999999))
        await set_code(phone, code)
        logging.basicConfig(level=logging.INFO)
        logging.info(f"VERIFICATION CODE FOR {phone}: {code}")
        try:
            return await send_sms_via_twilio(phone, f"Your code: {code}")
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone}: {e}")
            return False

    @classmethod
    async def verify_phone_code(cls, phone: str, code: str):
        saved_code = await get_code(phone)
        if not saved_code or saved_code != code:
            return False
        await delete_code(phone)
        return True

    @classmethod
    async def get_user_reputation(cls, user_id: int):
        user = await UserDAO.get_user_by_id(user_id)
        return user.reputation if user else 100

    @classmethod
    async def deduct_reputation(cls, user_id: int, amount: int):
        user = await UserDAO.get_user_by_id(user_id)
        reputation = max(60, min(100, user.reputation - amount))
        await UserDAO.update_reputation(user_id, reputation)
        return reputation

    @classmethod
    async def add_reputation(cls, user_id: int, amount: int):
        user = await UserDAO.get_user_by_id(user_id)
        reputation = max(60, min(100, user.reputation + amount))
        await UserDAO.update_reputation(user_id, reputation)
        return reputation
