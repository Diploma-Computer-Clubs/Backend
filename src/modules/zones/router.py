from typing import List

from fastapi import APIRouter, Depends

from src.modules.zones.schemas import SZoneCreate, SZoneGet
from src.modules.zones.service import ZoneService
from src.shared.dependencies.user_dependency import get_current_user_id

router = APIRouter(prefix='/zones', tags=['Work with zones'])

@router.post('/create_zone', summary='Create zone')
async def create_zone(zone_info: List[SZoneCreate], user_id: int = Depends(get_current_user_id)):
    return await ZoneService.create_zone(zone_info)

@router.get('/get_zones', summary='Get zones', response_model=List[SZoneGet])
async def get_club_zones(club_id: int, user_id: int = Depends(get_current_user_id)):
    return await ZoneService.get_club_zones(club_id)

@router.patch('/update_zone', summary='Update zone')
async def update_zone(zone_info: SZoneGet, user_id: int = Depends(get_current_user_id)):
    return True