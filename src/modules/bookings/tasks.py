import asyncio

from src.shared.celery.app import celery_app


@celery_app.task(name="bookings.deactivate_no_show")
def deactivate_booking_if_no_show(booking_id: int):
    from src.modules.bookings.service import BookingService

    asyncio.run(BookingService.process_no_show(booking_id))


@celery_app.task(name="bookings.restore_reputation")
def restore_reputation_task(user_id: int):
    from src.modules.users.service import UserService

    asyncio.run(UserService.add_reputation(user_id, 4))
