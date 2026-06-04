from celery import Celery
from src.modules.users.model import User
from src.modules.cities.model import City
from src.modules.clubs.model import Club
from src.modules.zones.model import Zone
from src.modules.computers.model import Computer
from src.modules.bookings.model import Booking
from src.modules.pricing.model import ZonePackage
from src.modules.club_staff.model import ClubStaff
from src.modules.map_objects.model import MapObject

from src.shared.configurations.config import get_redis_url

celery_app = Celery(
    "diploma_project",
    broker=get_redis_url(),
    backend=get_redis_url(),
    include=["src.modules.bookings.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_transport_options={
        "visibility_timeout": 60 * 24 * 3600,
    },
)
