from typing import Optional

from pydantic import BaseModel


class SComputersCreate(BaseModel):
    number: int
    specification: str
    zone_id: int
    x: Optional[float] = None
    y: Optional[float] = None

class SComputerGet(BaseModel):
    id: int
    number: int
    specification: str
    is_active: bool
    zone_id: int
    x: Optional[float] = None
    y: Optional[float] = None