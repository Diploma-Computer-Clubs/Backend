from fastapi import Depends, HTTPException
from src.modules.users.dependencies import get_current_user
from src.modules.users.schemas import SUser, SUserGetData, SUserGetCity, SUserPostData
from fastapi import APIRouter
from src.modules.users.model import User
from src.modules.users.service import UserService
from fastapi import Response
from src.shared.auth.jwt import set_auth_cookies
from src.shared.dependencies.user_dependency import get_current_user_id

router = APIRouter(prefix='/users', tags=['Work with users'])


@router.post("/registration", summary="Registration")
async def register_user(user_data: SUser, response: Response):
    user = await UserService.register_new_user(user_data)
    if not user:
        raise HTTPException(status_code=409, detail='User already exists')

    access, refresh = set_auth_cookies(response, user.id)
    return {"access_token": access, "refresh_token": refresh}


@router.get("/find_user")
async def get_user_by_filter(phone_number: str):
    user = await UserService.find_user_by_phone_number(phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User found", "user": user.phone_number}


@router.patch("/reset-password")
async def reset_password(phone: str, new_password: str, response: Response):
    user = await UserService.reset_password(phone, new_password)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    set_auth_cookies(response, user.id)
    return {"status": "success", "message": "Password reset successful"}


@router.get("/me", summary="Give info about user", response_model = SUserGetData)
async def get_me(user_data: User = Depends(get_current_user)):
    return user_data


@router.get("/{city_id}", summary="Give users city_id", response_model=SUserGetCity)
async def get_me(user_city_id: User = Depends(get_current_user)):
    return user_city_id


@router.patch('/change_user', summary='Change users name and city')
async def change_user(user_data: SUserPostData, user: int = Depends(get_current_user)):
    return await UserService.change_user_data(user.id, user_data)