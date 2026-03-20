from typing import List

from fastapi import APIRouter, HTTPException

from src.modules.cities.schemas import SCityAdd, SCityUpdDesc, SCityCoordinates
from src.modules.cities.service import CityService

router = APIRouter(prefix='/cities', tags=['Work with cities'])


@router.post("/add", summary="Adding city")
async def add_city(city: SCityAdd):
    new_city = await CityService.adding_city(city)
    if not new_city:
        raise HTTPException(status_code=400, detail="Error adding a city")
    return {"message": "City successfully added"}


@router.patch("/update", summary="Updating city")
async def update_city(city: SCityUpdDesc):
    success = await CityService.update_city(city)
    if not success:
        raise HTTPException(status_code=404, detail='City does not exist')
    return {"message": "City updated successfully"}


@router.delete("/delete/{city_id}", summary="Deleting city")
async def delete_city(city_id: int):
    success = await CityService.delete_city(city_id)
    if not success:
        raise HTTPException(status_code=404, detail='City does not exist')
    return {"message": "City deleted successfully"}


@router.get('/get_all_cities', summary="Getting all cities", response_model=list[SCityUpdDesc])
async def gel_all_cities():
    return await CityService.get_all_cities()


@router.get('/get_cities_coordinates', summary='Get cities coordinates', response_model=List[SCityCoordinates])
async def get_cities_coordinates(city_id: int):
    return await CityService.get_cities_coordinates(city_id)