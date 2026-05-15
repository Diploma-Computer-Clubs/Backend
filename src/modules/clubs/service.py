import asyncio
import json
import logging
from datetime import datetime, timedelta

from sqlalchemy import func
from starlette import status
from starlette.websockets import WebSocket

from src.modules.clubs.schemas import SClubCreate, SClubChange, WSPeriodPayload, SZoneMapResponse
from src.modules.clubs.dao import ClubDAO
from src.shared.service.coordinate_service import CoordinatesService

logger = logging.getLogger(__name__)


class ClubService:

    @classmethod
    async def _get_club_coordinates(cls, city_name: str, address: str):
        full_address = f"{city_name}, {address}"
        try:
            return await CoordinatesService.get_coordinates_2gis(full_address)
        except Exception as e:
            logger.error(f"Failed to fetch coordinates for {full_address}: {e}")
            return None, None

    @classmethod
    async def create_club(cls, club_info: SClubCreate, user_id: int):
        lat, lon = await cls._get_club_coordinates(club_info.city_name, club_info.address)

        club_data = club_info.model_dump()
        club_data.pop("city_name", None)
        club_data.update({
            "latitude": lat,
            "longitude": lon,
            "owner_id": user_id
        })

        return await ClubDAO.add(**club_data)

    @classmethod
    async def get_clubs(cls):
        return await ClubDAO.find_all()

    @classmethod
    async def get_club(cls, club_id: int):
        return await ClubDAO.get_club_with_zones(club_id)

    @classmethod
    async def get_clubs_by_city(cls, city_id: int):
        return await ClubDAO.find_full_data(city_id=city_id)

    @classmethod
    async def get_clubs_count(cls, city_id: int):
        return await ClubDAO.count(city_id=city_id)

    @classmethod
    async def delete_clubs(cls, club_id: int):
        result = await ClubDAO.delete(id=club_id)
        return result > 0

    @classmethod
    async def get_club_by_id(cls, club_id: int):
        return await ClubDAO.find_one_or_none(id=club_id)

    @classmethod
    async def update_club(cls, club_info: SClubChange) -> bool:
        lat, lon = await cls._get_club_coordinates(club_info.city_name, club_info.address)

        club_data = club_info.model_dump()
        club_id = club_data.pop("id", None)
        club_data.pop("city_name", None)

        club_data.update({
            "latitude": lat,
            "longitude": lon,
            "updated_at": func.now()
        })

        result = await ClubDAO.update(filter_by={"id": club_id}, **club_data)
        return result > 0

    @classmethod
    async def get_club_min_price(cls, club_id: int):
        min_price = await ClubDAO.get_min_price_by_club(club_id)
        return min_price if min_price is not None else 0

    @classmethod
    async def get_club_map(cls, club_id: int, start_time: datetime, end_time: datetime):
        return await ClubDAO.get_zones_with_computers_status(club_id, start_time, end_time)

    @classmethod
    async def get_club_by_owner_id(cls, owner_id: int):
        return await ClubDAO.find_all(owner_id=owner_id)

    @classmethod
    async def handle_admin_websocket(cls, websocket: WebSocket, club_id: int):
        import contextlib
        from starlette.websockets import WebSocketDisconnect

        current_mode = "live"
        custom_start = None
        custom_end = None
        local_tz = datetime.now().astimezone().tzinfo

        def is_socket_open() -> bool:
            application_state = getattr(getattr(websocket, "application_state", None), "name", None)
            client_state = getattr(getattr(websocket, "client_state", None), "name", None)
            return application_state != "DISCONNECTED" and client_state != "DISCONNECTED"

        async def safe_close(code: int = status.WS_1000_NORMAL_CLOSURE, reason: str | None = None):
            if not is_socket_open():
                return
            try:
                if reason is None:
                    await websocket.close(code=code)
                else:
                    await websocket.close(code=code, reason=reason)
            except Exception:
                pass

        def normalize_client_datetime(value: datetime | None) -> datetime | None:
            if value is None:
                return None
            if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
                return value.replace(tzinfo=None)
            if local_tz is None:
                return value.astimezone().replace(tzinfo=None)
            return value.astimezone(local_tz).replace(tzinfo=None)

        async def send_map_update():
            nonlocal current_mode, custom_start, custom_end

            if not is_socket_open():
                return False

            try:
                if current_mode == "live":
                    now = datetime.now(local_tz).replace(tzinfo=None) if local_tz else datetime.now()
                    start, end = now, now + timedelta(hours=3)
                else:
                    start, end = custom_start, custom_end

                raw_zones = await cls.get_club_map(club_id, start, end)
                data_to_send = []
                if raw_zones:
                    for zone in raw_zones:
                        try:
                            validated_zone = SZoneMapResponse.model_validate(zone)
                            data_to_send.append(validated_zone.model_dump(by_alias=True, mode="json"))
                        except Exception:
                            if hasattr(SZoneMapResponse, "from_orm"):
                                validated_zone = SZoneMapResponse.from_orm(zone)
                                data_to_send.append(json.loads(validated_zone.json(by_alias=True)))
                            else:
                                data_to_send.append({k: v for k, v in zone.__dict__.items() if not k.startswith("_")})

                if not is_socket_open():
                    return False

                await websocket.send_json({
                    "mode": current_mode,
                    "start_time": start.isoformat(),
                    "end_time": end.isoformat(),
                    "zones": data_to_send
                })
                return True
            except WebSocketDisconnect:
                return False
            except Exception as e:
                logger.error(f"WebSocket map update failed: {e}", exc_info=True)
                if is_socket_open():
                    with contextlib.suppress(Exception):
                        await websocket.send_json({"error": f"Internal mapping error: {str(e)}"})
                    await safe_close(code=status.WS_1011_INTERNAL_ERROR)
                return False

        async def apply_period_payload(payload_json: dict):
            nonlocal current_mode, custom_start, custom_end

            try:
                command = WSPeriodPayload(**payload_json)
                if command.mode == "live":
                    current_mode, custom_start, custom_end = "live", None, None
                elif command.mode == "history" and command.start_time and command.end_time:
                    current_mode = "history"
                    custom_start = normalize_client_datetime(command.start_time)
                    custom_end = normalize_client_datetime(command.end_time)
                else:
                    if is_socket_open():
                        await websocket.send_json({"error": "Missing start_time or end_time for history mode"})
                    return True
                return await send_map_update()
            except (ValueError, TypeError):
                if is_socket_open():
                    await websocket.send_json({"error": "Validation failed or invalid JSON format"})
                return True

        async def auto_refresh_loop():
            try:
                while True:
                    await asyncio.sleep(1)
                    if not is_socket_open():
                        break
                    should_continue = await send_map_update()
                    if not should_continue:
                        break
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.error("WebSocket auto refresh loop crashed", exc_info=True)
                await safe_close(code=status.WS_1011_INTERNAL_ERROR)

        initial_payload = getattr(websocket.state, "ws_initial_payload", None)
        if not isinstance(initial_payload, dict):
            query_mode = websocket.query_params.get("mode")
            query_start = websocket.query_params.get("start_time")
            query_end = websocket.query_params.get("end_time")
            if query_mode or query_start or query_end:
                initial_payload = {
                    "mode": query_mode or ("history" if query_start and query_end else "live"),
                    "start_time": query_start,
                    "end_time": query_end,
                }
        setattr(websocket.state, "ws_initial_payload", None)
        if isinstance(initial_payload, dict) and any(
            key in initial_payload for key in ("mode", "start_time", "end_time")
        ):
            should_continue = await apply_period_payload(initial_payload)
            if not should_continue:
                return
        else:
            should_continue = await send_map_update()
            if not should_continue:
                return

        refresh_task = asyncio.create_task(auto_refresh_loop())

        try:
            while True:
                raw_data = await websocket.receive_text()
                try:
                    payload_json = json.loads(raw_data)
                    if not isinstance(payload_json, dict):
                        raise ValueError
                except (json.JSONDecodeError, ValueError, TypeError):
                    if is_socket_open():
                        await websocket.send_json({"error": "Validation failed or invalid JSON format"})
                    continue

                should_continue = await apply_period_payload(payload_json)
                if not should_continue:
                    break
        except WebSocketDisconnect:
            pass
        except RuntimeError as e:
            if "disconnect" not in str(e).lower() and "close" not in str(e).lower():
                logger.error("Unexpected WebSocket runtime error", exc_info=True)
                await safe_close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            logger.error("Unexpected WebSocket session error", exc_info=True)
            await safe_close(code=status.WS_1011_INTERNAL_ERROR)
        finally:
            refresh_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await refresh_task
            await safe_close()
