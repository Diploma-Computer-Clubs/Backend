import os
import uuid
import shutil
from fastapi import UploadFile


class MediaService:
    UPLOAD_DIR = "static/clubs"

    @classmethod
    async def save_image(cls, file: UploadFile) -> str:
        os.makedirs(cls.UPLOAD_DIR, exist_ok=True)

        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(cls.UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return f"/{file_path}"