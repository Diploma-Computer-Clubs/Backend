from fastapi import Depends, HTTPException
from src.modules.users.dao import UserDAO
from src.shared.auth.dependencies import get_current_user
from src.modules.users.schemas import SUser, SUserGetData
from src.modules.users.rb import RBUser
from fastapi import APIRouter

from src.modules.users.users import User

router = APIRouter(prefix='/users', tags=['Work with users'])

@router.get("/", summary="Get all users")
async def get_all_users(response_body: RBUser = Depends()) -> list[SUser]:
    return await UserDAO.find_all(**response_body.to_dict())


@router.get("/{id}", summary="Get user by id", response_model=SUserGetData)
async def get_user_by_id(user_id: int):
    result = await UserDAO.find_full_data(user_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return result


@router.get("/by_filter", summary="Get user by filtered data")
async def get_user_by_filter(request_body: RBUser = Depends()) -> SUser | dict:
    result = await UserDAO.find_one_or_none(**request_body.to_dict())
    if result is None:
        return {'message': f'User not found'}
    return result


@router.get("/me/", summary="Give info about user", response_model = SUserGetData)
async def get_me(user_data: User = Depends(get_current_user)):
    return user_data