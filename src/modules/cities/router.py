from typing import List

from fastapi import APIRouter, HTTPException, Depends

from src.modules.cities.schemas import SCityAdd, SCityUpdDesc, SCityCoordinates
from src.modules.cities.service import CityService
from src.shared.dependencies.dependencies import super_admin_only
from src.shared.dependencies.user_dependency import get_current_user_id

router = APIRouter(prefix='/cities', tags=['Cities management'])


@router.post("/", summary="Add new city (superadmin)")
async def add_city(city: SCityAdd):
    new_city = await CityService.adding_city(city)
    if not new_city:
        raise HTTPException(status_code=400, detail="Error adding a city")
    return {"message": "City successfully added"}

@router.patch("/{city_id}", summary="Update city details (superadmin)")
async def update_city(city: SCityUpdDesc, user_id: int = Depends(super_admin_only)):
    success = await CityService.update_city(city)
    if not success:
        raise HTTPException(status_code=404, detail='City does not exist')
    return {"message": "City updated successfully"}

@router.delete("/{city_id}", summary="Delete city (superadmin)")
async def delete_city(city_id: int, user_id: int = Depends(super_admin_only)):
    success = await CityService.delete_city(city_id)
    if not success:
        raise HTTPException(status_code=404, detail='City does not exist')
    return {"message": "City deleted successfully"}


@router.get("/", summary="Get all cities", response_model=list[SCityUpdDesc])
async def gel_all_cities():
    return await CityService.get_all_cities()

@router.get("/{city_id}/coordinates", summary="Get city coordinates", response_model=SCityCoordinates)
async def get_cities_coordinates(city_id: int):
    return await CityService.get_cities_coordinates(city_id)