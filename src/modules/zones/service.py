from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.modules.zones.dao import ZoneDAO
from src.modules.zones.schemas import SZoneCreate


class ZoneService:

    @classmethod
    async def create_zone(cls, zone_info: List[SZoneCreate]):
        data_to_insert = [zone.model_dump() for zone in zone_info]
        try:
            new_zone = await ZoneDAO.add_list(data_to_insert)
            return new_zone

        except IntegrityError:
            raise HTTPException(
                status_code=409
            )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Invalid error"
            )

    @classmethod
    async def get_club_zones(cls, club_id: int):
        return await ZoneDAO.find_all(club_id=club_id)