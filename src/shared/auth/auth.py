from passlib.context import CryptContext

from jose import jwt
from datetime import datetime, timedelta, timezone
from src.shared.configurations.config import get_auth_data
from src.modules.users.dao import UserDAO
from fastapi import Response

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def set_auth_cookies(response: Response, user_id: int):
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = create_refresh_token({"sub": str(user_id)})

    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    response.set_cookie(key="users_refresh_token", value=refresh_token, httponly=True)

    return access_token, refresh_token


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire, "type": "access"})
    auth_data = get_auth_data()
    return jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire, "type": "refresh"})
    auth_data = get_auth_data()
    return jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])


async def authenticate_user(phone_num: str, password: str):
    user = await UserDAO.find_one_or_none(phone_number=phone_num)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
