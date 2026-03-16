from fastapi import Depends, HTTPException, status
from src.shared.dependencies.user_dependency import get_current_user_id
from src.modules.users.dao import UserDAO
from src.modules.users.model import User

async def get_current_user(user_id: int = Depends(get_current_user_id)) -> User:
    user = await UserDAO.find_full_data(user_id)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not enough rights')
    return current_user
