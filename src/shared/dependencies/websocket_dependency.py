# src/clubs/dependencies.py
from fastapi import WebSocket, WebSocketException, status

from src.modules.club_staff.service import ClubStaffService
from src.modules.clubs.service import ClubService
from src.modules.users.dao import UserDAO
# Импортируем вашу функцию декодирования токена
from src.shared.utils.auth_utils import get_user_id_from_token


async def get_ws_club_admin(websocket: WebSocket, club_id: int, token: str) -> dict:
    """
    Кастомная проверка роли администратора для WebSocket-соединений.
    Использует get_user_id_from_token напрямую без HTTPBearer.
    """
    if not token:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Token missing")

    # 1. Декодируем токен вашей готовой функцией
    try:
        user_id = await get_user_id_from_token(token, "access")
    except Exception:
        # Если токен просрочен, невалиден или get_user_id_from_token выкинул ошибку
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired token")

    # 2. Проверка пользователя в БД
    user = await UserDAO.get_user_by_id(user_id)
    if not user:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
    # 3. Проверка существования клуба
    club = await ClubService.get_club_by_id(club_id)
    if not club:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Club not found")

    # 4. Проверка прав доступа (Владелец клуба)
    if club.owner_id == user.id:
        return {"role": "owner", "user_id": user.id}

    # 5. Проверка прав доступа (Сотрудник со статусом admin)
    staff_member = await ClubStaffService.get_member_by_club(user_id=user.id, club_id=club_id)

    if staff_member and staff_member.staff_role == "admin":
        return {"role": "admin", "user_id": user.id}

    # Если не владелец и не админ — закрываем соединение
    raise WebSocketException(
        code=status.WS_1008_POLICY_VIOLATION,
        reason="Access denied. Admin or Owner only."
    )
