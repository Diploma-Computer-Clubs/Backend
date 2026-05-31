from typing import List

from fastapi import APIRouter, UploadFile, File, Depends

from src.modules.media.schemas import SImageGet
from src.modules.media.service import MediaService
from src.shared.dependencies.dependencies import RoleChecker

router = APIRouter(prefix='/media', tags=['Media Management'])

@router.post("/images", summary="Upload image (owner)")
async def upload_image(file: UploadFile = File(...), auth: int = Depends(RoleChecker([]))):
    image_path = await MediaService.save_image(file)
    return {"image_url": image_path}

@router.get('/images', summary="Get images list", response_model=List[SImageGet])
async def get_images():
    return await MediaService.get_images()
