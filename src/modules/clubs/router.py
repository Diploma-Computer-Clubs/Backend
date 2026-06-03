from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Depends

from src.modules.clubs.schemas import SClubCreate, SClubMainInfo, SClubMap, SClubChange, SZoneMapResponse, \
    WSPeriodPayload
from src.modules.clubs.service import ClubService
from src.shared.dependencies.dependencies import RoleChecker, owner_only
from src.shared.dependencies.user_dependency import get_current_user_id


import json
import asyncio
from datetime import datetime, timedelta
from fastapi import APIRouter, WebSocket, WebSocketException, status, Depends
from typing import List

from src.shared.dependencies.websocket_dependency import get_ws_club_admin

router = APIRouter(prefix='/clubs', tags=['Clubs Management'])


@router.post("", summary="Register new club (role: owner)")
async def register_club(club_info: SClubCreate, user_info: int = Depends(owner_only), user_id: int = Depends(get_current_user_id)):
    result = await ClubService.create_club(club_info, user_id)
    if not result:
        raise HTTPException(status_code=400, detail="Error adding a club")
    return {"message": "Club successfully added"}

@router.patch("/{club_id}", summary="Update club info (owner)")
async def update_club(club_info: SClubChange, user_id: int = Depends(RoleChecker([]))):
    return await ClubService.update_club(club_info)

@router.delete("/{club_id}", summary="Delete club (owner)")
async def delete_club(club_id: int, user_id: int = Depends(RoleChecker([]))):
    return await ClubService.delete_clubs(club_id)


@router.get("/map", summary="Get clubs for map view", response_model=List[SClubMap])
async def get_clubs_map(city_id: int):
    return await ClubService.get_clubs_by_city(city_id)

@router.get("/search", summary="Get clubs list by city", response_model=List[SClubMainInfo])
async def get_main_info(city_id: int):
    result = await ClubService.get_clubs_by_city(city_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"No clubs found in city {city_id}")
    return result

@router.get("/count", summary="Get total clubs count in city")
async def get_clubs_count(city_id: int):
    count = await ClubService.get_clubs_count(city_id)
    return {"city_id": city_id, "total_clubs": count}

@router.get("/clubs", summary="Get detailed clubs info", response_model=List[SClubMainInfo])
async def get_clubs_info(user_id: int = Depends(get_current_user_id)):
    return await ClubService.get_clubs(user_id)

@router.get("/{club_id}", summary="Get detailed club info", response_model=SClubMainInfo)
async def get_club_info(club_id: int):
    result = await ClubService.get_club(club_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Club {club_id} not found")
    return result

@router.get("/{club_id}/min-price", summary="Get minimum zone price")
async def get_min_price(club_id: int):
    min_price = await ClubService.get_club_min_price(club_id)
    if min_price is None:
        raise HTTPException(status_code=404, detail="Club not found")
    return {"club_id": club_id, "min_price": min_price}

@router.get("/{club_id}/availability", summary="Get computers availability map", response_model=List[SZoneMapResponse])
async def get_club_availability(club_id: int, start_time: datetime, end_time: datetime):
    zones = await ClubService.get_club_map(club_id, start_time, end_time)
    if not zones:
        raise HTTPException(404, detail="Zones not found for this club")
    return zones

#вебсокет
@router.websocket("/{club_id}/availability/ws")
async def ws_club_availability(websocket: WebSocket, club_id: int):
    await websocket.accept()
    try:
        await get_ws_club_admin(websocket, club_id)
    except WebSocketException as e:
        if getattr(getattr(websocket, "application_state", None), "name", None) != "DISCONNECTED":
            try:
                await websocket.close(code=e.code, reason=e.reason)
            except Exception:
                pass
        return

    await ClubService.handle_admin_websocket(websocket, club_id)


from fastapi.responses import Response
from src.modules.clubs.schemas import SClubStatisticsDatePeriod


@router.post("/{club_id}/statistics/export", summary="Export club statistics (owner)")
async def export_club_statistics(club_id: int, period: SClubStatisticsDatePeriod, user_id: int = Depends(RoleChecker([]))):
    content, file_name = await ClubService.export_club_statistics_by_date(club_id, period)
    return Response(
        content=content,
        media_type="application/vnd.ms-excel",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'}
    )
