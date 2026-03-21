from typing import List

from fastapi import APIRouter, Depends

from src.modules.computers.schemas import SComputersCreate
from src.modules.computers.service import ComputerService
from src.shared.dependencies.user_dependency import get_current_user_id

router = APIRouter(prefix="/computers", tags=["Work with computers"])

@router.post('/create_computers', summary='Create computers')
async def create_computers(computers: List[SComputersCreate], user_id: int = Depends(get_current_user_id)):
    return await ComputerService.create_computers(computers)