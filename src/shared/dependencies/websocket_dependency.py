from fastapi import WebSocket, WebSocketException, status

from src.modules.club_staff.service import ClubStaffService
from src.modules.clubs.service import ClubService
from src.modules.users.dao import UserDAO
from src.shared.utils.auth_utils import get_user_id_from_token


async def get_ws_club_admin(websocket: WebSocket, club_id: int, token: str = None) -> dict:
    def extract_bearer_token(raw_value: str | None) -> str | None:
        if not raw_value:
            return None
        raw_value = raw_value.strip()
        if not raw_value:
            return None
        if raw_value.lower().startswith("bearer "):
            raw_value = raw_value[7:].strip()
        return raw_value or None

    token = extract_bearer_token(token)

    if not token:
        token = extract_bearer_token(websocket.headers.get("authorization"))

    if not token:
        token = extract_bearer_token(websocket.headers.get("sec-websocket-protocol"))

    if not token:
        for cookie_name in ("access_token", "authorization", "Authorization", "token"):
            token = extract_bearer_token(websocket.cookies.get(cookie_name))
            if token:
                break

    if not token:
        token = extract_bearer_token(websocket.query_params.get("token"))

    if not token:
        import json

        try:
            raw_auth_message = await websocket.receive_text()
        except Exception:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Token missing")

        raw_auth_message = raw_auth_message.strip()
        auth_payload = None

        if raw_auth_message:
            try:
                auth_payload = json.loads(raw_auth_message)
            except json.JSONDecodeError:
                auth_payload = None

            if isinstance(auth_payload, dict):
                token = (
                    extract_bearer_token(auth_payload.get("token"))
                    or extract_bearer_token(auth_payload.get("access_token"))
                    or extract_bearer_token(auth_payload.get("authorization"))
                )
                extra_payload = {
                    key: value
                    for key, value in auth_payload.items()
                    if key not in {"token", "access_token", "authorization", "token_type", "type"}
                }
                if extra_payload:
                    setattr(websocket.state, "ws_initial_payload", extra_payload)
            else:
                token = extract_bearer_token(raw_auth_message)

    if not token:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Token missing")

    try:
        user_id = await get_user_id_from_token(token, "access")
    except Exception:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired token")

    user = await UserDAO.get_user_by_id(user_id)
    if not user:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")

    club = await ClubService.get_club_by_id(club_id)
    if not club:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Club not found")

    if club.owner_id == user.id:
        return {"role": "owner", "user_id": user.id}

    staff_member = await ClubStaffService.get_member_by_club(user_id=user.id, club_id=club_id)

    if staff_member and staff_member.staff_role == "admin":
        return {"role": "admin", "user_id": user.id}

    raise WebSocketException(
        code=status.WS_1008_POLICY_VIOLATION,
        reason="Access denied. Admin or Owner only."
    )
