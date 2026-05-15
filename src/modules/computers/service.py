from typing import List

from sqlalchemy import func

from src.modules.computers.dao import ComputerDAO
from src.modules.computers.schemas import SComputersCreate

class ComputerService:

    @classmethod
    async def create_computers(cls, computers: List[SComputersCreate]):
        data_to_insert = [comp.model_dump() for comp in computers]
        return await ComputerDAO.add_list(data_to_insert)

    @classmethod
    async def get_computers(cls, zone_id: int):
        return await ComputerDAO.find_all(zone_id=zone_id)

    @classmethod
    async def turn_on_computer(cls, computer_id: int):
        result = await ComputerDAO.update(filter_by={"id": computer_id}, is_active=True, updated_at=func.now())
        return result > 0

    @classmethod
    async def turn_off_computer(cls, computer_id: int):
        result = await ComputerDAO.update(filter_by={"id": computer_id}, is_active=False, updated_at=func.now())
        return result > 0

    @classmethod
    async def delete_computer(cls, computer_id: int):
        return await ComputerDAO.delete(id=computer_id)