from sqlalchemy import func

from src.modules.cities.dao import CityDAO
from src.modules.cities.schemas import SCityAdd, SCityUpdDesc
from src.shared.service.coordinate_service import CoordinatesService


class CityService:

    @classmethod
    async def adding_city(cls, city: SCityAdd):
        lat, lon = await CoordinatesService.get_coordinates_2gis(city.city)

        city_data = city.model_dump()
        city_data.update({"latitude": lat, "longitude": lon})

        return await CityDAO.add(**city_data)

    @classmethod
    async def update_city(cls, city: SCityUpdDesc) -> bool:
        lat, lon = await CoordinatesService.get_coordinates_2gis(city.city)

        city_data = city.model_dump()
        city_data.update({
            "latitude": lat,
            "longitude": lon,
            "updated_at": func.now()
        })

        city_id = city_data.pop('id')

        result = await CityDAO.update(filter_by={'id': city_id}, **city_data)
        return result > 0

    @classmethod
    async def delete_city(cls, city_id: int) -> bool:
        result = await CityDAO.delete(id=city_id)
        return result > 0

    @classmethod
    async def get_all_cities(cls):
        return await CityDAO.find_all()

    @classmethod
    async def get_cities_coordinates(cls, city_id: int):
        return await CityDAO.find_one_or_none(id=city_id)