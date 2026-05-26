import math
from typing import List
from src.modules.pricing.dao import PackageDAO
from src.modules.pricing.schemas import SBulkPriceRequest

from datetime import datetime, timedelta


class PricingService:
    @classmethod
    async def calculate_price(cls, zone_id: int, start: datetime, end: datetime) -> int:
        start, end = start.replace(tzinfo=None), end.replace(tzinfo=None)
        total_hours = math.ceil((end - start).total_seconds() / 3600)
        if total_hours <= 0:
            return 0
        packages = await PackageDAO.find_all(zone_id=zone_id)
        if not packages:
            return 0
        base_hour = next((p for p in packages if not p.is_package and p.duration == 1), None)
        base_price = base_hour.price
        dp = [float('inf')] * (total_hours + 1)
        dp[0] = 0
        for i in range(1, total_hours + 1):
            current_dt = start + timedelta(hours=i - 1)
            current_time = current_dt.time()
            for p in packages:
                is_applicable = False
                hours_covered = 1
                if p.start_time and p.end_time:
                    p_start, p_end = p.start_time, p.end_time
                    in_window = False
                    if p_start <= p_end:
                        in_window = p_start <= current_time < p_end
                    else:
                        in_window = current_time >= p_start or current_time < p_end
                    if in_window:
                        is_applicable = True
                        limit = p.duration if p.duration else 24
                        hours_covered = min(limit, total_hours - i + 1)
                else:
                    is_applicable = True
                    hours_covered = p.duration if p.duration else 1
                if is_applicable:
                    next_idx = min(total_hours, i + int(hours_covered) - 1)
                    dp[next_idx] = min(dp[next_idx], dp[i - 1] + p.price)
            dp[i] = min(dp[i], dp[i - 1] + base_price)
        return int(dp[total_hours])

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

    @classmethod
    def get_booking_payment_stats(cls, packages, start: datetime, end: datetime):
        start, end = start.replace(tzinfo=None), end.replace(tzinfo=None)
        total_hours = math.ceil((end - start).total_seconds() / 3600)
        if total_hours <= 0 or not packages:
            return {}

        base_hour = next((p for p in packages if not p.is_package and p.duration == 1), None)
        if not base_hour:
            return {}

        dp = [float('inf')] * (total_hours + 1)
        used = [[] for _ in range(total_hours + 1)]
        dp[0] = 0

        for i in range(1, total_hours + 1):
            current_dt = start + timedelta(hours=i - 1)
            current_time = current_dt.time()

            for p in packages:
                is_applicable = False
                hours_covered = 1

                if p.start_time and p.end_time:
                    p_start, p_end = p.start_time, p.end_time
                    in_window = False

                    if p_start <= p_end:
                        in_window = p_start <= current_time < p_end
                    else:
                        in_window = current_time >= p_start or current_time < p_end

                    if in_window:
                        is_applicable = True
                        hours_covered = min(p.duration if p.duration else 24, total_hours - i + 1)
                else:
                    is_applicable = True
                    hours_covered = p.duration if p.duration else 1

                if is_applicable:
                    next_idx = min(total_hours, i + int(hours_covered) - 1)
                    new_price = dp[i - 1] + p.price

                    if new_price < dp[next_idx]:
                        dp[next_idx] = new_price
                        used[next_idx] = used[i - 1] + [p.name]

            base_price = dp[i - 1] + base_hour.price
            if base_price < dp[i]:
                dp[i] = base_price
                used[i] = used[i - 1] + [base_hour.name]

        result = {}
        for package_name in used[total_hours]:
            result[package_name] = result.get(package_name, 0) + 1

        return result

    @classmethod
    def get_booking_payment_details(cls, packages, start: datetime, end: datetime):
        stats = cls.get_booking_payment_stats(packages, start, end)
        package_prices = {package.name: package.price for package in packages}
        result = {}

        for package_name, count in stats.items():
            result[package_name] = {
                "count": count,
                "price": package_prices.get(package_name, 0)
            }

        return result
