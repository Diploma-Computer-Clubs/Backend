from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.shared.utils.auth_utils import get_user_id_from_token

security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = credentials.credentials

    return await get_user_id_from_token(token, "access")

async def get_user_id_for_reset(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    token = credentials.credentials
    return await get_user_id_from_token(token, "reset_password")