import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException

class MediaService:
    UPLOAD_DIR = Path("static/clubs")

    @classmethod
    async def save_image(cls, file: UploadFile) -> str:
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        extension = file.filename.split(".")[-1].lower()
        if extension not in ["jpg", "jpeg", "png", "webp"]:
            raise HTTPException(status_code=400, detail="Invalid file extension")

        unique_filename = f"{uuid.uuid4()}.{extension}"
        file_path = cls.UPLOAD_DIR / unique_filename

        with file_path.open("wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return f"/{file_path.as_posix()}"
