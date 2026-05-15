from datetime import datetime
from typing import List

from sqlalchemy import func

from src.modules.zones.dao import ZoneDAO
from src.modules.zones.schemas import SZoneCreate, SZoneGet


class ZoneService:

    @classmethod
    async def create_zones(cls, zone_info: List[SZoneCreate]):
        data_to_insert = [zone.model_dump() for zone in zone_info]

        return await ZoneDAO.add_list(data_to_insert)

    @classmethod
    async def get_club_zones(cls, club_id: int):
        return await ZoneDAO.find_all(club_id=club_id)

    @classmethod
    async def update_zones(cls, zones_info: List[SZoneGet]):
        current_time = datetime.now()

        data_to_update = []
        for zone in zones_info:
            zone_dict = zone.model_dump()
            zone_dict["updated_at"] = current_time
            data_to_update.append(zone_dict)
        return await ZoneDAO.update_list(data_to_update)

    @classmethod
    async def delete_zone(cls, zone_id: int):
        return await ZoneDAO.delete(id=zone_id)