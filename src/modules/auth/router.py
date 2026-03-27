from fastapi import Depends, HTTPException

from src.modules.auth.dependencies import get_current_user_id_by_refresh
from src.modules.auth.schemas import SUserAuth
from fastapi import APIRouter

from src.modules.auth.service import AuthService
from src.shared.auth.jwt import set_auth_tokens, create_access_token, create_refresh_token

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post("/login")
async def login_user(user_data: SUserAuth):
    user = await AuthService.login_user(user_data.phone_number, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong login or password")

    access = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer"
    }


@router.post("/refresh")
async def refresh_token(user_id: int = Depends(get_current_user_id_by_refresh)):
    return set_auth_tokens(user_id)
