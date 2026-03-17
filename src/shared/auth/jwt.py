from jose import jwt
from datetime import datetime, timedelta, timezone
from src.shared.configurations.config import get_auth_data
from fastapi import Response


def set_auth_cookies(response: Response, user_id: int):
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = create_refresh_token({"sub": str(user_id)})

    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    response.set_cookie(key="users_refresh_token", value=refresh_token, httponly=True)

    return access_token, refresh_token


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

def delete_auth_cookies(response: Response):
    response.delete_cookie(key="users_access_token")
    response.delete_cookie(key="users_refresh_token")