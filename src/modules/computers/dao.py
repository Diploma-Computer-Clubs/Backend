from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.modules.zones.model import Zone
from src.shared.configurations.database import async_session_maker
from src.shared.dao.base import BaseDAO
from src.modules.computers.model import Computer

class ComputerDAO(BaseDAO):
    model = Computer

    @classmethod
    async def find_computer_in_club(cls, computer_id: int, zone_id: int, club_id: int):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .join(Zone, cls.model.zone_id == Zone.id)
                .filter(
                    cls.model.id == computer_id,
                    cls.model.zone_id == zone_id,
                    Zone.club_id == club_id
                )
            )
            result = await session.execute(query)
            return result.scalars().first()