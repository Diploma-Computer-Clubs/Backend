from typing import List

from fastapi import APIRouter, Depends

from src.modules.computers.schemas import SComputersCreate, SComputerGet
from src.modules.computers.service import ComputerService
from src.shared.dependencies.user_dependency import get_current_user_id

router = APIRouter(prefix="/computers", tags=["Computers Management"], dependencies=[Depends(get_current_user_id)])

@router.post("/", summary="Create new computers")
async def create_computers(computers: List[SComputersCreate]):
    return await ComputerService.create_computers(computers)

@router.get("/", summary="Get computers in zone", response_model=List[SComputerGet])
async def get_computers(zone_id: int):
    return await ComputerService.get_computers(zone_id)

@router.post("/{computer_id}/turn-on", summary="Power on computer")
async def turn_on_computer(computer_id: int):
    return await ComputerService.turn_on_computer(computer_id)

@router.post("/{computer_id}/turn-off", summary="Power off computer")
async def turn_off_computer(computer_id: int):
    return await ComputerService.turn_off_computer(computer_id)
