from typing import List

from fastapi import APIRouter, Depends

from src.modules.zones.schemas import SZoneCreate, SZoneGet
from src.modules.zones.service import ZoneService
from src.shared.dependencies.user_dependency import get_current_user_id

router = APIRouter(prefix='/zones', tags=['Zones Management'])

@router.post("/", summary="Create new zones")
async def create_zones(zone_info: List[SZoneCreate], user_id: int = Depends(get_current_user_id)):
    return await ZoneService.create_zones(zone_info)

@router.get("/", summary="Get club zones", response_model=List[SZoneGet])
async def get_club_zones(club_id: int, user_id: int = Depends(get_current_user_id)):
    return await ZoneService.get_club_zones(club_id)

@router.patch("/{zone_id}", summary="Update zone details")
async def update_zone(zone_id: int, zone_info: SZoneGet, user_id: int = Depends(get_current_user_id)):

    return {"status": True}
