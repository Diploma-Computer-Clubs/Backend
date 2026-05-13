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


    #Вебсокет
    @classmethod
    async def handle_admin_websocket(cls, websocket: WebSocket, club_id: int):
        """Вся логика сессии вебсокета: стейты, отправка, циклы и фоновые таски"""
        current_mode = "live"
        custom_start = None
        custom_end = None

        async def send_map_update():
            nonlocal current_mode, custom_start, custom_end
            try:
                if current_mode == "live":
                    now = datetime.now()
                    start, end = now, now + timedelta(hours=3)
                else:
                    start, end = custom_start, custom_end

                # Запрос к твоему DAO
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
                                data_to_send.append({k: v for k, v in zone.__dict__.items() if not k.startswith('_')})

                await websocket.send_json({
                    "mode": current_mode,
                    "start_time": start.isoformat(),
                    "end_time": end.isoformat(),
                    "zones": data_to_send
                })
            except Exception as e:
                logger.error(f"!!! КРАШ СЕРИАЛИЗАЦИИ В ВЕБСОКЕТЕ !!!: {str(e)}", exc_info=True)
                try:
                    await websocket.send_json({"error": f"Internal mapping error: {str(e)}"})
                    await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
                except Exception:
                    pass

        async def auto_refresh_loop():
            try:
                while True:
                    await asyncio.sleep(30)
                    if current_mode == "live":
                        await send_map_update()
            except asyncio.CancelledError:
                pass
            except Exception:
                await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

        # Отправляем карту сразу после коннекта
        await send_map_update()
        refresh_task = asyncio.create_task(auto_refresh_loop())

        try:
            while True:
                raw_data = await websocket.receive_text()
                try:
                    payload_json = json.loads(raw_data)
                    command = WSPeriodPayload(**payload_json)
                    if command.mode == "live":
                        current_mode, custom_start, custom_end = "live", None, None
                    elif command.mode == "history" and command.start_time and command.end_time:
                        current_mode, custom_start, custom_end = "history", command.start_time, command.end_time
                    else:
                        await websocket.send_json({"error": "Missing start_time or end_time for history mode"})
                        continue
                    await send_map_update()
                except (json.JSONDecodeError, ValueError):
                    await websocket.send_json({"error": "Validation failed or invalid JSON format"})
        except Exception:
            pass
        finally:
            refresh_task.cancel()
            try:
                await websocket.close()
            except Exception:
                pass