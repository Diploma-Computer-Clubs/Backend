import math
from typing import List
from src.modules.pricing.dao import PackageDAO
from src.modules.pricing.schemas import SBulkPriceRequest

from datetime import datetime, timedelta


class PricingService:
    @classmethod
    async def calculate_price(cls, zone_id: int, start: datetime, end: datetime) -> int:
        # 1. Подготовка данных
        start, end = start.replace(tzinfo=None), end.replace(tzinfo=None)
        total_hours = math.ceil((end - start).total_seconds() / 3600)

        if total_hours <= 0:
            return 0

        packages = await PackageDAO.find_all(zone_id=zone_id)
        if not packages:
            return 0

        # Базовая цена за час (фолбэк)
        base_hour = next((p for p in packages if not p.is_package and p.duration == 1), None)
        base_price = base_hour.price if base_hour else 500

        # dp[i] — минимальная стоимость за первые i часов брони
        dp = [float('inf')] * (total_hours + 1)
        dp[0] = 0

        for i in range(1, total_hours + 1):
            # Текущая метка времени, для которой ищем лучший тариф
            current_dt = start + timedelta(hours=i - 1)
            current_time = current_dt.time()

            for p in packages:
                # Определяем, сколько часов этот пакет может "закрыть" в нашей брони
                # Для обычных комбо (без времени) — это p.duration
                # Для временных (Day/Night) — это количество часов от current_dt до конца окна пакета

                is_applicable = False
                hours_covered = 1  # по умолчанию для Hourly Fix

                if p.start_time and p.end_time:
                    # ЛОГИКА ВРЕМЕННЫХ ПАКЕТОВ (Day Pass, Night Package)
                    p_start, p_end = p.start_time, p.end_time

                    # Проверяем, входит ли ТЕКУЩИЙ час в окно пакета
                    in_window = False
                    if p_start <= p_end:
                        in_window = p_start <= current_time < p_end
                    else:  # Ночной переход
                        in_window = current_time >= p_start or current_time < p_end

                    if in_window:
                        is_applicable = True
                        # Вычисляем, сколько часов брони от текущего момента i
                        # этот пакет может закрыть (но не больше своей duration)
                        # Это и позволяет "досидеть до конца пакета" или уйти раньше
                        limit = p.duration if p.duration else 24
                        hours_covered = min(limit, total_hours - i + 1)
                else:
                    # ЛОГИКА УНИВЕРСАЛЬНЫХ ПАКЕТОВ (Combo 3h, Hourly Fix)
                    is_applicable = True
                    hours_covered = p.duration if p.duration else 1

                if is_applicable:
                    # Прыгаем вперед: обновляем стоимость для точки (текущий час + сколько покрыли)
                    next_idx = min(total_hours, i + int(hours_covered) - 1)

                    # Если мы используем пакет, он закрывает все часы до next_idx за свою цену
                    # Стоимость в точке next_idx = цена до пакета + цена пакета
                    dp[next_idx] = min(dp[next_idx], dp[i - 1] + p.price)

            # Фолбэк (на всякий случай)
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
