from pydantic import BaseModel, ConfigDict


class SMapObjectCreate(BaseModel):
    type: str
    label: str
    x: float
    y: float
    width: float
    height: float
    rotation: float


class SMapObjectUpdate(BaseModel):
    type: str
    label: str
    x: float
    y: float
    width: float
    height: float
    rotation: float


class SMapObjectGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    label: str
    x: float
    y: float
    width: float
    height: float
    rotation: float
    club_id: int
