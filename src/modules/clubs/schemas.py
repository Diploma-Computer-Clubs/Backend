from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional


class SBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class SPromoItem(SBase):
    title: str = Field(..., description="Название акции (например, 3 + 2)")
    value: str = Field(..., description="Ценность (например, 1000 тг)")

class SZoneShort(SBase):
    id: int
    name: str
    cost: int

class SBookingShort(SBase):
    id: int
    start_time: datetime
    end_time: datetime
    total_price: int
    is_checked_in: bool
    full_name: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def get_user_name(cls, data):
        user = getattr(data, 'user', None)
        if user:
            setattr(data, 'full_name', getattr(user, 'full_name', None))
        return data

class SComputerShort(SBase):
    id: int
    number: int
    is_active: bool = Field(alias="is_Active")
    x: Optional[float] = None
    y: Optional[float] = None
    bookings: List[SBookingShort] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class SClubBase(SBase):
    name: str
    address: str
    image_url: str
    image_price_url: Optional[str] = None
    img_background: Optional[str] = None
    promos: List[SPromoItem] = []
    description: str
    city_id: int

class SClubCreate(SClubBase):
    rating: float = Field(default=5.0, ge=0, le=5)
    city_name: str

class SClubChange(SBase):
    id: int
    name: Optional[str] = None
    address: Optional[str] = None
    image_url: Optional[str] = None
    image_price_url: Optional[str] = None
    img_background: Optional[str] = None
    rating: Optional[int] = None
    promos: Optional[List[SPromoItem]] = None
    description: Optional[str] = None
    city_id: Optional[int] = None
    city_name: Optional[str] = None

class SClubMainInfo(SClubBase):
    id: int
    rating: float
    zones: List[SZoneShort] = []

class SClubMap(SBase):
    id: int
    name: str
    image_url: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class SZoneMapResponse(SBase):
    id: int
    name: str
    x: Optional[float] = None
    y: Optional[float] = None
    computers: List[SComputerShort]

#вебсокет
class WSPeriodPayload(BaseModel):
    mode: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class SClubStatisticsPeriod(BaseModel):
    start_time: datetime
    end_time: datetime


class SClubStatisticsDatePeriod(BaseModel):
    start_date: date
    end_date: date
