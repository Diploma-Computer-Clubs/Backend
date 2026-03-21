from pydantic import Field, BaseModel
from src.shared.schemas.schemas import ZoneName


class SZoneCreate(BaseModel):
    name: ZoneName = Field(..., description="Zone name")
    cost: int = Field(..., description="Zone cost")
    cpu: str = Field(..., description="Zone cpu")
    gpu: str = Field(..., description="Zone gpu")
    ram: str = Field(..., description="Zone ram")
    ssd: str = Field(..., description="Zone ssd")
    monitor: str = Field(..., description="Zone monitor")
    club_id: int = Field(..., description="Zone club ID")

class SZoneGet(BaseModel):
    name: ZoneName = Field(..., description="Zone name")
    cost: int = Field(..., description="Zone cost")
    cpu: str = Field(..., description="Zone cpu")
    gpu: str = Field(..., description="Zone gpu")
    ram: str = Field(..., description="Zone ram")
    ssd: str = Field(..., description="Zone ssd")
    monitor: str = Field(..., description="Zone monitor")