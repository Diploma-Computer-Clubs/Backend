from fastapi import APIRouter, UploadFile, File

from src.modules.media.schemas import SImageGet
from src.modules.media.service import MediaService

router = APIRouter(prefix='/media', tags=['Media Management'])

@router.post("/images", summary="Upload image")
async def upload_image(file: UploadFile = File(...)):
    image_path = await MediaService.save_image(file)
    return {"image_url": image_path}

@router.get('/images', summary="Get images list", response_model=SImageGet)
async def get_images():
    return {"status": True}