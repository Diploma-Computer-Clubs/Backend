from datetime import datetime
from typing import List

from src.modules.pricing.dao import PackageDAO
from src.modules.pricing.schemas import SBulkPriceRequest


class PricingService:
    @classmethod
    async def calculate_price(cls, zone_id: int, start: datetime, end: datetime) -> int:
        packages = await PackageDAO.find_all(zone_id=zone_id)
        base_hour = next((p for p in packages if not p.is_package and p.duration == 1), None)
        duration_hours = (end - start).total_seconds() / 3600
        best_price = int(duration_hours * base_hour.price if hasattr(base_hour, 'price') else base_hour)
        u_start, u_end = start.time().replace(second=0, microsecond=0), end.time().replace(second=0, microsecond=0)
        for p in packages:
            if p.is_package and p.start_time and p.end_time:
                if u_start >= p.start_time and u_end <= p.end_time: best_price = min(best_price, p.price)
        return best_price

    @classmethod
    async def calculate_bulk_price(cls, data: List[SBulkPriceRequest]):
        grand_total = 0

        for entry in data:
            for item in entry.items:
                price_per_one = await cls.calculate_price(
                    item.zone_id,
                    entry.start_time,
                    entry.end_time
                )
                grand_total += price_per_one * item.count

        return {"total_amount": grand_total}