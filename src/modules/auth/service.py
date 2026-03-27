from src.modules.auth.auth import authenticate_user


class AuthService:

    @classmethod
    async def login_user(cls, phone: str, password: str):
        user = await authenticate_user(phone, password)
        if not user:
            return None
        return user

    @classmethod
    async def refresh_token(cls, user_id: int):
        return user_id

