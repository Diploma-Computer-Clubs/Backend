from fastapi import APIRouter, UploadFile, File, Depends

from src.modules.media.schemas import SImageGet
from src.modules.media.service import MediaService
from src.shared.dependencies.user_dependency import get_current_user_id

router = APIRouter(prefix='/media', tags=['Work with media'])

@router.post("/upload")
async def upload_club_image(file: UploadFile = File(...), user_id: int = Depends(get_current_user_id)):
    image_path = await MediaService.save_image(file)
    return {"image_url": image_path}

@router.get('/get_image', response_model=SImageGet)
async def get_image():
    return True