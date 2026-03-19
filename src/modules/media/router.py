from fastapi import APIRouter, UploadFile, File

from src.modules.media.service import MediaService

router = APIRouter(prefix='/media', tags=['Work with media'])

@router.post("/upload")
async def upload_club_image(file: UploadFile = File(...)):
    image_path = await MediaService.save_image(file)
    return {"image_url": image_path}