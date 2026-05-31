from typing import List

from fastapi import APIRouter, Depends

from src.modules.computers.schemas import SComputersCreate, SComputerGet, SComputerUpdate
from src.modules.computers.service import ComputerService
from src.shared.dependencies.dependencies import RoleChecker

router = APIRouter(prefix="/computers", tags=["Computers Management"])

@router.post("/", summary="Create new computers (owner)")
async def create_computers(computers: List[SComputersCreate], auth: int = Depends(RoleChecker([]))):
    return await ComputerService.create_computers(computers)

@router.get("/", summary="Get computers in zone", response_model=List[SComputerGet])
async def get_computers(zone_id: int):
    return await ComputerService.get_computers(zone_id)

@router.patch("/{computer_id}", summary="Update computer (owner)")
async def update_computer(computer_id: int, computer: SComputerUpdate, auth: int = Depends(RoleChecker([]))):
    return await ComputerService.update_computer(computer_id, computer)

@router.post("/{computer_id}/turn-on", summary="Power on computer (admin, owner)")
async def turn_on_computer(computer_id: int, auth: int = Depends(RoleChecker(["admin"]))):
    return await ComputerService.turn_on_computer(computer_id)

@router.post("/{computer_id}/turn-off", summary="Power off computer (admin, owner)")
async def turn_off_computer(computer_id: int, auth: int = Depends(RoleChecker(["admin"]))):
    return await ComputerService.turn_off_computer(computer_id)

@router.delete("/{computer_id}", summary="Delete computer (owner)")
async def delete_computer(computer_id: int, auth: int = Depends(RoleChecker([]))):
    return await ComputerService.delete_computer(computer_id)