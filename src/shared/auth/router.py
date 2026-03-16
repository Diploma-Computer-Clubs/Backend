from fastapi import Depends
from src.modules.users.dao import UserDAO
from src.shared.auth.dependencies import get_current_user_by_refresh
from src.modules.users.schemas import SUser
from src.shared.auth.schemas import SUserAuth
from fastapi import APIRouter, HTTPException, status
from src.shared.auth.auth import get_password_hash, authenticate_user, set_auth_cookies
from fastapi import Response

from src.modules.users.model import User

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post("/registration", summary="Create new user")
async def register_user(user_data: SUser):
    user = await UserDAO.find_one_or_none(phone_number=user_data.phone_number)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')
    user_dict = user_data.model_dump()
    user_dict['password'] = get_password_hash(user_data.password_hash)
    await UserDAO.add(**user_dict)
    return {'message': 'User successfully created'}


@router.post("/login", summary="Login user")
async def login_user(response: Response, user_data: SUserAuth):
    user = await authenticate_user(phone_num=user_data.phone_number, password=user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail='Wrong login or password')
    access, refresh = set_auth_cookies(response, user.id)
    return {'access_token': access, 'refresh_token': refresh}


@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    response.delete_cookie(key="users_refresh_token")
    return {'message': 'User successfully logged out'}


@router.post("/refresh")
async def refresh_token(response: Response, user: User = Depends(get_current_user_by_refresh)):
    set_auth_cookies(response, user.id)
    return {"message": "Tokens updated"}