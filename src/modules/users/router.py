from fastapi import Depends, HTTPException, status
from src.modules.auth.auth import get_password_hash
from src.modules.users.dao import UserDAO
from src.modules.users.dependencies import get_current_user
from src.modules.users.schemas import SUser, SUserGetData
from src.modules.users.rb import RBUser
from fastapi import APIRouter
from src.modules.users.model import User

router = APIRouter(prefix='/users', tags=['Work with users'])

@router.post("/registration", summary="Create new user")
async def register_user(user_data: SUser):
    user = await UserDAO.find_one_or_none(phone_number=user_data.phone_number)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')
    user_dict = user_data.model_dump()
    user_dict['password'] = get_password_hash(user_data.password_hash)
    await UserDAO.add(**user_dict)
    return {'message': 'User successfully created'}

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