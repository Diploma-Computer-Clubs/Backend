from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.shared.utils.auth_utils import get_user_id_from_token

security = HTTPBearer()


async def get_current_user_id_by_refresh(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    if not credentials:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    token = credentials.credentials

    user_id = await get_user_id_from_token(token, "refresh")

    return user_id
