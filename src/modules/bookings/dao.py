from src.shared.dao.base import BaseDAO
from src.modules.bookings.model import Booking

class BookingDAO(BaseDAO):
    model = Booking