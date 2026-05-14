# src/clubs/dependencies.py
import logging

from fastapi import WebSocket, WebSocketException, status

from src.modules.club_staff.service import ClubStaffService
from src.modules.clubs.service import ClubService
from src.modules.users.dao import UserDAO
# Импортируем вашу функцию декодирования токена
from src.shared.utils.auth_utils import get_user_id_from_token


logger = logging.getLogger(__name__)

async def get_ws_club_admin(websocket: WebSocket, club_id: int, token: str) -> dict:
    logger.info(f"[CHECK] Starting get_ws_club_admin for club_id={club_id}")

    # 1. Декодирование JWT
    try:
        logger.info("[CHECK] Decoding token via get_user_id_from_token...")
        user_id = await get_user_id_from_token(token, "access")
        logger.info(f"[CHECK] Token decoded successfully. Extracted user_id={user_id}")
    except Exception as e:
        logger.error(f"[CHECK FAILED] Token decoding crashed. Error: {str(e)}", exc_info=True)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Token expired or invalid")

    # 2. Проверка пользователя в БД
    logger.info(f"[CHECK] Fetching user from DB for user_id={user_id}...")
    user = await UserDAO.get_user_by_id(user_id)
    if not user:
        logger.warning(f"[CHECK FAILED] User with id={user_id} not found in database.")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
    logger.info(f"[CHECK] User found in DB: {user.id}")

    # 3. Проверка существования клуба
    logger.info(f"[CHECK] Fetching club from DB for club_id={club_id}...")
    club = await ClubService.get_club_by_id(club_id)
    if not club:
        logger.warning(f"[CHECK FAILED] Club with id={club_id} not found in database.")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Club not found")
    logger.info(f"[CHECK] Club found in DB: ID={club.id}, Owner_ID={club.owner_id}")

    # 4. Проверка прав доступа (Владелец клуба)
    if club.owner_id == user.id:
        logger.info(f"[CHECK SUCCESS] Access GRANTED. User {user.id} is the OWNER of club {club_id}")
        return {"role": "owner", "user_id": user.id}

    # 5. Проверка прав доступа (Сотрудник со статусом admin)
    logger.info(f"[CHECK] User is not owner. Checking staff role for user_id={user.id}, club_id={club_id}...")
    staff_member = await ClubStaffService.get_member_by_club(user_id=user.id, club_id=club_id)

    if staff_member:
        logger.info(f"[CHECK] Staff member found. Role in DB: '{staff_member.staff_role}'")
        if staff_member.staff_role == "admin":
            logger.info(f"[CHECK SUCCESS] Access GRANTED. User {user.id} is an ADMIN in club {club_id}")
            return {"role": "admin", "user_id": user.id}
    else:
        logger.info(f"[CHECK] No staff member record found for user {user.id} in club {club_id}")

    # Если не владелец и не админ
    logger.warning(f"[CHECK FAILED] Access DENIED. User {user.id} has no rights for club {club_id}")
    raise WebSocketException(
        code=status.WS_1008_POLICY_VIOLATION,
        reason="Access denied. Admin or Owner only."
    )