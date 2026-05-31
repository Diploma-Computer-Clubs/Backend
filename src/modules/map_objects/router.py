from typing import List

from fastapi import APIRouter, Depends

from src.modules.map_objects.schemas import SMapObjectCreate, SMapObjectGet, SMapObjectUpdate
from src.modules.map_objects.service import MapObjectService
from src.shared.dependencies.dependencies import RoleChecker

router = APIRouter(prefix='/map-objects', tags=['Map Objects'])


@router.get("/{club_id}/map-objects/", summary="Get club map objects", response_model=List[SMapObjectGet])
async def get_map_objects(club_id: int):
    return await MapObjectService.get_by_club(club_id)


@router.post("/{club_id}/map-objects/", summary="Create map object (owner)")
async def create_map_object(club_id: int, data: SMapObjectCreate, auth: int = Depends(RoleChecker([]))):
    return await MapObjectService.create(club_id, data)


@router.patch("/{object_id}", summary="Update map object (owner)")
async def update_map_object(object_id: int, data: SMapObjectUpdate, auth: int = Depends(RoleChecker([]))):
    return await MapObjectService.update(object_id, data)


@router.delete("/{object_id}", summary="Delete map object (owner)")
async def delete_map_object(object_id: int, auth: int = Depends(RoleChecker([]))):
    return await MapObjectService.delete(object_id)
