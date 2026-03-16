from fastapi import Request, HTTPException
from src.shared.utils.auth_utils import get_user_id_from_token


async def get_current_user_id_by_refresh(request: Request) -> int:
    token = request.cookies.get('users_refresh_token')
    if not token: raise HTTPException(status_code=401)
    return await get_user_id_from_token(token, "refresh")
