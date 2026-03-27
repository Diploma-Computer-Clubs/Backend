from pydantic import BaseModel


class SImageGet(BaseModel):
    name: str
    path: str