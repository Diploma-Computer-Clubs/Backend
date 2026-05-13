from typing import List

from src.modules.zones.dao import ZoneDAO
from src.modules.zones.schemas import SZoneCreate


class ZoneService:

    @classmethod
    async def create_zones(cls, zone_info: List[SZoneCreate]):
        data_to_insert = [zone.model_dump() for zone in zone_info]

        return await ZoneDAO.add_list(data_to_insert)

    @classmethod
    async def get_club_zones(cls, club_id: int):
        return await ZoneDAO.find_all(club_id=club_id)