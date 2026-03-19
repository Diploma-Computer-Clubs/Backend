from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from src.modules.cities.dao import CityDAO
from src.modules.cities.schemas import SCityAdd, SCityUpdDesc
from src.shared.service.coordinate_service import CoordinatesService


class CityService:

    @classmethod
    async def adding_city(cls, city: SCityAdd):
        lat, lon = await CoordinatesService.get_coordinates_2gis(city.city)
        city_data = city.model_dump()
        city_data["latitude"] = lat
        city_data["longitude"] = lon

        try:
            new_city = await CityDAO.add(**city_data)
            return new_city

        except IntegrityError:
            raise HTTPException(
                status_code=409,
                detail=f"City '{city.city}' already exists",
            )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Invalid error"
            )

    @classmethod
    async def update_city(cls, city: SCityUpdDesc):
        result = await CityDAO.update(
            filter_by={'id': city.id},
            city=city.city,
            updated_at=func.now()
        )
        return result > 0

    @classmethod
    async def delete_city(cls, city_id: int):
        result = await CityDAO.delete(id=city_id)
        return result > 0

    @classmethod
    async def get_all_cities(cls):
        return await CityDAO.find()

    @classmethod
    async def get_cities_coordinates(cls, city_id: int):
        return await CityDAO.find_all(id=city_id)