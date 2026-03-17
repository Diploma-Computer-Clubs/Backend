from fastapi import HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext

from src.shared.configurations.config import get_auth_data

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_id_from_token(token: str, expected_type: str) -> int:
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=401, detail='Token is not valid')

    if payload.get("type") != expected_type:
        raise HTTPException(status_code=401, detail=f"Not {expected_type} Token")

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=401, detail='User id not found')

    return int(user_id)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

