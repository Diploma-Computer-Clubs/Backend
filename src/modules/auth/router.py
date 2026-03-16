from fastapi import Depends
from src.modules.auth.dependencies import get_current_user_id_by_refresh
from src.modules.auth.schemas import SUserAuth
from fastapi import APIRouter, HTTPException
from src.modules.auth.auth import authenticate_user, set_auth_cookies
from fastapi import Response

router = APIRouter(prefix='/auth', tags=['Auth'])


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
async def refresh_token(response: Response, user: int = Depends(get_current_user_id_by_refresh)):
    set_auth_cookies(response, user)
    return {"message": "Tokens updated"}