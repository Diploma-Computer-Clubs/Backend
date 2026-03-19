from typing import List

from fastapi import APIRouter, HTTPException, Depends
from src.modules.clubs.schemas import SClubCreate, SClubMainInfo, SClubMap
from src.modules.clubs.service import ClubService
from src.shared.dependencies.user_dependency import get_current_user_id

router = APIRouter(prefix='/clubs', tags=['Work with clubs'])


@router.post('/register', summary='Register a new club')
async def register_club(club_info: SClubCreate):
    result = await ClubService.create_club(club_info)
    if not result:
        raise HTTPException(status_code=400, detail="Error adding a club")
    return {"message": "Club successfully added"}


@router.get('/get_clubs_map', summary='Get clubs on map', response_model=List[SClubMap])
async def get_clubs_map(city_id: int, user_id: int = Depends(get_current_user_id)):
    return await ClubService.get_clubs_by_city(city_id)


@router.get('/get_main_info', summary='Get main info about clubs in city', response_model=list[SClubMainInfo])
async def get_main_info(city_id: int, user_id: int = Depends(get_current_user_id)):
    result = await ClubService.get_clubs_by_city(city_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"in city with ID {city_id} clubs not found"
        )
    return result


@router.get('/get_clubs_count', summary='Get count of clubs in city')
async def get_clubs_count(city_id: int, user_id: int = Depends(get_current_user_id)):
    count = await ClubService.get_clubs_count(city_id)
    return {"city_id": city_id, "total_clubs": count}


@router.get('/get_club_info', summary='Get main info about club', response_model=SClubMainInfo)
async def get_main_info(club_id: int, user_id: int = Depends(get_current_user_id)):
    result = await ClubService.get_club(club_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"{club_id} club not found"
        )
    return result