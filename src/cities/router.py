from fastapi import APIRouter

from src.cities.dao import CityDAO
from src.cities.schemas import SCityAdd, SCityUpdDesc

router = APIRouter(prefix='/cities', tags=['Work with cities'])

@router.post("/add/")
async def add_city(city: SCityAdd) -> dict:
    check = await CityDAO.add(**city.dict())
    if check:
        return {"message": "Город успешно добавлен", "major": city}
    else:
        return {"message": "Ошибка при добавлении города"}

@router.put("/update/")
async def update_city(city: SCityUpdDesc) -> dict:
    check = await CityDAO.update(filter_by={'id': city.id},
                                   city=city.city)
    if check:
        return {"message": "Город обновлен успешно", "city": city}
    else:
        return {"message": "Ошибка при обновлении города"}

@router.delete("/delete/{major_id}")
async def delete_major(city_id: int) -> dict:
    check = await CityDAO.delete(id=city_id)
    if check:
        return {"message": f"Город с ID {city_id} удален!"}
    else:
        return {"message": "Ошибка при удалении города"}