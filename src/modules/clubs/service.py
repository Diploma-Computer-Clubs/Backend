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
    async def get_clubs(cls, user_id: int):
        return await ClubDAO.get_clubs(user_id)

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

        club_data = club_info.model_dump(exclude_unset=True)
        club_id = club_data.pop("id", None)
        club_data.pop("city_name", None)

        club_data.update({
            "latitude": lat,
            "longitude": lon,
            "updated_at": func.now()
        })
        club_data["updated_at"] = func.now()

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

    @classmethod
    def _get_statistics_overlap_hours(cls, start_time: datetime, end_time: datetime, period_start: datetime, period_end: datetime):
        actual_start = max(start_time, period_start)
        actual_end = min(end_time, period_end)

        if actual_end <= actual_start:
            return 0

        return (actual_end - actual_start).total_seconds() / 3600

    @classmethod
    def _build_statistics_excel(cls, club_name: str, start_time: datetime, end_time: datetime, total_amount: float, rows: list[list]):
        from xml.sax.saxutils import escape

        xml = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<?mso-application progid="Excel.Sheet"?>',
            '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">',
            '<Worksheet ss:Name="Statistics">',
            '<Table>',
        ]

        table_rows = [
            ["Club", club_name],
            ["Start time", start_time.strftime("%Y-%m-%d")],
            ["End time", end_time.strftime("%Y-%m-%d")],
            [],
            ["Zone", "Zone total amount", "Computer", "Occupied hours", "Free hours", "Payment type", "Usage count", "Computer total amount"],
        ]

        table_rows.extend(rows)

        for row in table_rows:
            xml.append('<Row>')
            for value in row:
                if isinstance(value, (int, float)):
                    xml.append(f'<Cell><Data ss:Type="Number">{value}</Data></Cell>')
                else:
                    xml.append(f'<Cell><Data ss:Type="String">{escape("" if value is None else str(value))}</Data></Cell>')
            xml.append('</Row>')

        xml.extend([
            '</Table>',
            '</Worksheet>',
            '</Workbook>',
        ])

        return ''.join(xml).encode("utf-8")

    @classmethod
    async def export_club_statistics(cls, club_id: int, period):
        from src.modules.pricing.service import PricingService

        start_time = period.start_time.replace(tzinfo=None)
        end_time = period.end_time.replace(tzinfo=None)
        now = datetime.now()

        if end_time > now:
            end_time = now

        if end_time < start_time:
            end_time = start_time

        club = await cls.get_club_by_id(club_id)
        zones = await ClubDAO.get_club_statistics_data(club_id, start_time, end_time)
        period_hours = cls._get_statistics_overlap_hours(start_time, end_time, start_time, end_time)
        rows = []
        total_amount = 0

        for zone in sorted(zones, key=lambda item: (item.name, item.id)):
            zone_total_amount = 0
            zone_rows = []

            for computer in sorted(zone.computers, key=lambda item: (item.number, item.id)):
                occupied_hours = 0
                computer_total_amount = 0
                payment_stats = {}

                for booking in sorted(computer.bookings, key=lambda item: item.start_time):
                    booking_start = max(booking.start_time, start_time)
                    booking_end = min(booking.end_time, end_time)
                    overlap_hours = cls._get_statistics_overlap_hours(booking.start_time, booking.end_time, start_time, end_time)

                    if overlap_hours <= 0:
                        continue

                    occupied_hours += overlap_hours

                    booking_hours = cls._get_statistics_overlap_hours(booking.start_time, booking.end_time, booking.start_time, booking.end_time)
                    if booking_hours > 0:
                        computer_total_amount += booking.total_price * (overlap_hours / booking_hours)

                    booking_payment_stats = PricingService.get_booking_payment_stats(zone.packages, booking_start, booking_end)
                    for package_name, count in booking_payment_stats.items():
                        payment_stats[package_name] = payment_stats.get(package_name, 0) + count

                free_hours = max(period_hours - occupied_hours, 0)
                occupied_hours = round(occupied_hours, 2)
                free_hours = round(free_hours, 2)
                computer_total_amount = round(computer_total_amount, 2)
                zone_total_amount += computer_total_amount

                zone_rows.append({
                    "computer_name": f"{computer.number}",
                    "occupied_hours": occupied_hours,
                    "free_hours": free_hours,
                    "payment_stats": payment_stats,
                    "computer_total_amount": computer_total_amount,
                })

            zone_total_amount = round(zone_total_amount, 2)
            total_amount += zone_total_amount

            if not zone_rows:
                rows.append([zone.name, zone_total_amount, "", 0, round(period_hours, 2), "", 0, 0])
                continue

            for item in zone_rows:
                if item["payment_stats"]:
                    for package_name, count in sorted(item["payment_stats"].items()):
                        rows.append([
                            zone.name,
                            zone_total_amount,
                            item["computer_name"],
                            item["occupied_hours"],
                            item["free_hours"],
                            package_name,
                            count,
                            item["computer_total_amount"],
                        ])
                else:
                    rows.append([
                        zone.name,
                        zone_total_amount,
                        item["computer_name"],
                        item["occupied_hours"],
                        item["free_hours"],
                        "",
                        0,
                        item["computer_total_amount"],
                    ])

        file_name = f"club_{club_id}_statistics_{start_time.strftime('%Y%m%d_%H%M%S')}_{end_time.strftime('%Y%m%d_%H%M%S')}.xml"
        content = cls._build_statistics_excel(club.name if club else f"Club {club_id}", start_time, end_time, round(total_amount, 2), rows)
        return content, file_name

    @classmethod
    def _build_statistics_excel_by_date(cls, club_name: str, owner_name: str, start_date, end_date, total_amount: float, rows: list[list]):
        from xml.sax.saxutils import escape

        xml = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<?mso-application progid="Excel.Sheet"?>',
            '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">',
            '<Worksheet ss:Name="Statistics">',
            '<Table>',
        ]

        table_rows = [
            ["Club", club_name],
            ["Owner", owner_name],
            ["Start date", start_date.strftime("%Y-%m-%d")],
            ["End date", end_date.strftime("%Y-%m-%d")],
            [],
            ["Computer", "Zone", "Occupied hours", "Free hours", "Payment type", "Payment type price", "Usage count", "Computer total amount", "Zone total amount", "Total amount"],
        ]

        table_rows.extend(rows)

        for row in table_rows:
            xml.append('<Row>')
            for value in row:
                if isinstance(value, (int, float)):
                    xml.append(f'<Cell><Data ss:Type="Number">{value}</Data></Cell>')
                else:
                    xml.append(f'<Cell><Data ss:Type="String">{escape("" if value is None else str(value))}</Data></Cell>')
            xml.append('</Row>')

        xml.extend([
            '</Table>',
            '</Worksheet>',
            '</Workbook>',
        ])

        return ''.join(xml).encode("utf-8")

    @classmethod
    async def export_club_statistics_by_date(cls, club_id: int, period):
        from datetime import datetime, timedelta, time

        from src.modules.pricing.service import PricingService

        start_time = datetime.combine(period.start_date, time.min)
        end_time = datetime.combine(period.end_date + timedelta(days=1), time.min)
        now = datetime.now()

        if end_time > now:
            end_time = now

        if end_time < start_time:
            end_time = start_time

        club = await ClubDAO.get_club_with_owner(club_id)
        zones = await ClubDAO.get_club_statistics_data(club_id, start_time, end_time)
        period_hours = round(cls._get_statistics_overlap_hours(start_time, end_time, start_time, end_time), 2)
        total_amount = 0
        zones_data = []

        for zone in sorted(zones, key=lambda item: (item.name, item.id)):
            zone_total_amount = 0
            zone_rows = []

            for computer in sorted(zone.computers, key=lambda item: (item.number, item.id)):
                occupied_hours = 0
                computer_total_amount = 0
                payment_stats = {}

                for booking in sorted(computer.bookings, key=lambda item: item.start_time):
                    booking_start = max(booking.start_time, start_time)
                    booking_end = min(booking.end_time, end_time)
                    overlap_hours = cls._get_statistics_overlap_hours(booking.start_time, booking.end_time, start_time, end_time)

                    if overlap_hours <= 0:
                        continue

                    occupied_hours += overlap_hours

                    booking_hours = cls._get_statistics_overlap_hours(booking.start_time, booking.end_time, booking.start_time, booking.end_time)
                    if booking_hours > 0:
                        computer_total_amount += booking.total_price * (overlap_hours / booking_hours)

                    booking_payment_stats = PricingService.get_booking_payment_details(zone.packages, booking_start, booking_end)
                    for package_name, info in booking_payment_stats.items():
                        if package_name not in payment_stats:
                            payment_stats[package_name] = {"count": 0, "price": info["price"]}
                        payment_stats[package_name]["count"] += info["count"]

                occupied_hours = round(occupied_hours, 2)
                free_hours = round(max(period_hours - occupied_hours, 0), 2)
                computer_total_amount = round(computer_total_amount, 2)
                zone_total_amount += computer_total_amount

                if payment_stats:
                    first_payment_row = True
                    for package_name, info in sorted(payment_stats.items()):
                        zone_rows.append([
                            computer.number if first_payment_row else "",
                            zone.name if first_payment_row else "",
                            occupied_hours if first_payment_row else "",
                            free_hours if first_payment_row else "",
                            package_name,
                            info["price"],
                            info["count"],
                            computer_total_amount if first_payment_row else "",
                        ])
                        first_payment_row = False
                else:
                    zone_rows.append([
                        computer.number,
                        zone.name,
                        occupied_hours,
                        free_hours,
                        "",
                        "",
                        0,
                        computer_total_amount,
                    ])

            zone_total_amount = round(zone_total_amount, 2)
            total_amount += zone_total_amount
            zones_data.append({
                "zone_name": zone.name,
                "zone_total_amount": zone_total_amount,
                "zone_rows": zone_rows,
            })

        total_amount = round(total_amount, 2)
        rows = []
        first_total_row = True

        for zone_data in zones_data:
            zone_name = zone_data["zone_name"]
            zone_total_amount = zone_data["zone_total_amount"]
            zone_rows = zone_data["zone_rows"]

            if not zone_rows:
                rows.append(["", zone_name, 0, period_hours, "", "", 0, "", zone_total_amount, total_amount if first_total_row else ""])
                first_total_row = False
                continue

            first_zone_row = True
            for row in zone_rows:
                rows.append(row + [zone_total_amount if first_zone_row else "", total_amount if first_total_row else ""])
                first_zone_row = False
                first_total_row = False

        owner_name = club.owner.full_name if club and club.owner else ""
        club_name = club.name if club else f"Club {club_id}"
        file_name = f"club_{club_id}_statistics_{period.start_date.strftime('%Y%m%d')}_{period.end_date.strftime('%Y%m%d')}.xls"
        content = cls._build_statistics_excel_by_date(club_name, owner_name, period.start_date, period.end_date, total_amount, rows)
        return content, file_name
