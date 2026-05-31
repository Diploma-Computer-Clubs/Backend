from datetime import datetime

from src.modules.map_objects.dao import MapObjectDAO
from src.modules.map_objects.schemas import SMapObjectCreate, SMapObjectUpdate


class MapObjectService:

    @classmethod
    async def get_by_club(cls, club_id: int):
        return await MapObjectDAO.find_all(club_id=club_id)

    @classmethod
    async def create(cls, club_id: int, data: SMapObjectCreate):
        return await MapObjectDAO.add(club_id=club_id, **data.model_dump())

    @classmethod
    async def update(cls, object_id: int, data: SMapObjectUpdate):
        result = await MapObjectDAO.update(
            filter_by={"id": object_id},
            **data.model_dump(),
            updated_at=datetime.now(),
        )
        return result > 0

    @classmethod
    async def delete(cls, object_id: int):
        return await MapObjectDAO.delete(id=object_id)
