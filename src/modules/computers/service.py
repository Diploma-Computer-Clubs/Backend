from typing import List

from src.modules.computers.dao import ComputerDAO
from src.modules.computers.schemas import SComputersCreate
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

class ComputerService:

    @classmethod
    async def create_computers(cls, computers: List[SComputersCreate]):
        data_to_insert = [comp.model_dump() for comp in computers]
        try:
            new_comp = await ComputerDAO.add_list(data_to_insert)
            return new_comp

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
    async def get_computers(cls, zone_id: int):
        return await ComputerDAO.find_all(zone_id=zone_id)