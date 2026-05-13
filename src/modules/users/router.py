from fastapi import Depends, HTTPException
from src.shared.dependencies.dependencies import get_current_user
from src.modules.users.schemas import SUser, SUserGetData, SUserPostData, SUserVerify, SUserPhoneAuth
from fastapi import APIRouter
from src.modules.users.model import User
from src.modules.users.service import UserService
from src.shared.auth.jwt import set_auth_tokens, create_reset_password_token
from src.shared.dependencies.user_dependency import get_current_user_id, get_user_id_for_reset

router = APIRouter(prefix='/users', tags=['Users Management'])


@router.post("/registration", summary="Register new user")
async def register_user(user_data: SUser):
    user = await UserService.register_new_user(user_data)
    if not user:
        raise HTTPException(status_code=409, detail='User already exists')
    return set_auth_tokens(user.id)

@router.post("/verification-code", summary="Request SMS verification code")
async def send_sms(phone: SUserPhoneAuth):
    result = await UserService.request_verification(phone=phone.phone_number)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid phone")
    return {"status": "sent"}

@router.post("/verify-code", summary="Verify code and issue reset token")
async def verify(user_data: SUserVerify):
    is_verified = await UserService.verify_phone_code(user_data.phone_number, user_data.code)
    if not is_verified:
        raise HTTPException(status_code=400, detail="Invalid code")

    user = await UserService.find_user_by_phone_number(user_data.phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_reset_password_token({"sub": str(user.id)})
    return {"status": "verified", "reset_token": reset_token}

@router.patch("/password", summary="Reset user password")
async def reset_password(
        new_password: str, user_id: int = Depends(get_user_id_for_reset)):
    success = await UserService.reset_password_by_id(user_id, new_password)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or error updating")
    return {"status": "success", "message": "Password updated. Please log in."}



@router.get("/me", summary="Get current user profile", response_model=SUserGetData)
async def get_me(user_data: User = Depends(get_current_user)):
    return user_data

@router.patch('/me', summary='Update user profile data')
async def change_user(user_data: SUserPostData, user: int = Depends(get_current_user_id)):
    return await UserService.change_user_data(user, user_data)


@router.delete('/me', summary='Delete current user account')
async def delete_user(user_id: int = Depends(get_current_user_id)):
    return await UserService.delete_user(user_id)



@router.get("/search", summary="Find user by phone number")
async def get_user_by_filter(phone_number: str):
    user = await UserService.find_user_by_phone_number(phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User found", "user": user.phone_number}