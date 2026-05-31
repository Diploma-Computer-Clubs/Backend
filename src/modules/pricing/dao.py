from sqlalchemy import select

from src.modules.pricing.model import ZonePackage
from src.modules.zones.model import Zone
from src.shared.configurations.database import async_session_maker
from src.shared.dao.base import BaseDAO


class PackageDAO(BaseDAO):
    model = ZonePackage

    @classmethod
    async def find_by_club_id(cls, club_id: int):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .join(Zone, Zone.id == cls.model.zone_id)
                .filter(Zone.club_id == club_id)
            )
            result = await session.execute(query)
            return result.scalars().all()
