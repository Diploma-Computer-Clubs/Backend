from pydantic import BaseModel


class SComputersCreate(BaseModel):
    number: int
    specification: str
    is_Active: bool
    zone_id: int