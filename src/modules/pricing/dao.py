from src.modules.pricing.model import ZonePackage
from src.shared.dao.base import BaseDAO


class PackageDAO(BaseDAO):
    model = ZonePackage