from fastapi import Depends, HTTPException

from src.modules.auth.dependencies import get_current_user_id_by_refresh
from src.modules.auth.schemas import SUserAuth, SUserVerify, SUserPhoneAuth
from fastapi import APIRouter
from fastapi import Response

from src.modules.auth.service import AuthService
from src.shared.auth.jwt import set_auth_cookies, delete_auth_cookies

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    user = await AuthService.login_user(user_data.phone_number, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong login or password")

    access, refresh = set_auth_cookies(response, user.id)
    return {"access_token": access, "refresh_token": refresh}


@router.post("/logout")
async def logout_user(response: Response):
    delete_auth_cookies(response)
    return {"message": "User successfully logged out"}


@router.post("/refresh")
async def refresh_token(response: Response, user_id: int = Depends(get_current_user_id_by_refresh)):
    # user_id уже проверен зависимостью Depends
    access, refresh = set_auth_cookies(response, user_id)
    return {"access_token": access, "refresh_token": refresh}


@router.post("/verify")
async def verify(user_data: SUserVerify):
    is_verified = await AuthService.verify_phone_code(user_data.phone_number, user_data.code)
    if not is_verified:
        raise HTTPException(status_code=400, detail="Invalid code")
    return {"status": "verified"}


@router.post("/send-sms", summary="Sending sms")
async def send_sms(phone: SUserPhoneAuth):
    result = await AuthService.request_verification(phone=phone.phone_number)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid phone")
    return {"status": "sent"}