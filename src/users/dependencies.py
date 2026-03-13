from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
from datetime import datetime, timezone
from src.configurations.config import get_auth_data
from src.users.dao import UserDAO
from src.users.users import User


async def _verify_token(token: str, expected_type: str) -> User:
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is not valid')

    if payload.get("type") != expected_type:
        raise HTTPException(status_code=401, detail=f"Not {expected_type} Token")

    expire = payload.get('exp')
    if (not expire) or (datetime.fromtimestamp(int(expire), tz=timezone.utc) < datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User id not found')

    user = await UserDAO.find_full_data(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    return user


def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Access Token not found')
    return token


def get_refresh_token(request: Request):
    token = request.cookies.get('users_refresh_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh Token not found')
    return token


async def get_current_user(token: str = Depends(get_token)) -> User:
    return await _verify_token(token, "access")


async def get_current_user_by_refresh(token: str = Depends(get_refresh_token)) -> User:
    return await _verify_token(token, "refresh")


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not enough rights')
    return current_user
