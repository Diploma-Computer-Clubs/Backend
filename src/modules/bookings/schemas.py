from datetime import datetime, timedelta

from pydantic import BaseModel, model_validator, ConfigDict


class SBookingCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    total_price: int
    computer_id: int
    zone_id: int
    club_id: int

    @model_validator(mode='after')
    def check_time_diff(self) -> 'SBookingCreate':
        if self.end_time <= self.start_time:
            raise ValueError("End time must be before start time")

        if (self.end_time - self.start_time) < timedelta(hours=1):
            raise ValueError("Minimum time must be at least 1 hour")

        return self


class SClubInfo(BaseModel):
    name: str
    address: str
    image_url: str


class SZoneInfo(BaseModel):
    name: str


class SComputerInfo(BaseModel):
    number: int


class SBookingView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    total_price: int
    start_time: datetime
    end_time: datetime

    club: SClubInfo
    zone: SZoneInfo
    computer: SComputerInfo