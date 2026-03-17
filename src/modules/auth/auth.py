from src.modules.users.dao import UserDAO

from src.shared.utils.auth_utils import verify_password


async def authenticate_user(phone_num: str, password: str):
    user = await UserDAO.find_one_or_none(phone_number=phone_num)
    if not user or not verify_password(password, user.password):
        return None
    return user
