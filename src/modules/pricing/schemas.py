from pydantic import BaseModel, Field
from datetime import time, datetime
from typing import Optional, List


class SZonePackage(BaseModel):
    name: str
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration: int
    price: int
    is_package: bool = False
    zone_id: int

class SPriceItem(BaseModel):
    zone_id: int
    count: int

class SBulkPriceRequest(BaseModel):
    items: List[SPriceItem]
    start_time: datetime
    end_time: datetime

class SPriceDetail(BaseModel):
    zone_id: int
    price_per_computer: int
    subtotal: int

class SBulkPriceResponse(BaseModel):
    total_amount: int

class STotalPriceResponse(BaseModel):
    total_amount: int