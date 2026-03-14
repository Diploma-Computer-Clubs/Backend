from src.shared.dao.base import BaseDAO
from src.modules.cities.cities import City

class CityDAO(BaseDAO):
    model = City