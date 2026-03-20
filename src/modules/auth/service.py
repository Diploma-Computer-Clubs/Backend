import random

from src.modules.auth.auth import authenticate_user
from src.shared.redis.utils import set_code, get_code, delete_code
from src.shared.utils.sms_sender import send_sms_via_twilio


class AuthService:

    @classmethod
    async def login_user(cls, phone: str, password: str):
        user = await authenticate_user(phone, password)
        if not user:
            return None
        return user

    @classmethod
    async def request_verification(cls, phone: str):
        code = str(random.randint(100000, 999999))
        await set_code(phone, code)
        sent = await send_sms_via_twilio(phone, f"Code: {code}")
        return sent

    @classmethod
    async def verify_phone_code(cls, phone: str, code: str):
        saved_code = await get_code(phone)
        if not saved_code or saved_code != code:
            return False

        await delete_code(phone)
        return True

    @classmethod
    async def refresh_token(cls, user_id: int):
        return user_id

