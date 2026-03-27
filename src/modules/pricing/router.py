from typing import List

from fastapi import APIRouter, Depends

from src.modules.pricing.dao import PackageDAO
from src.modules.pricing.schemas import SBulkPriceRequest, SZonePackage, STotalPriceResponse
from src.modules.pricing.service import PricingService
from src.shared.dependencies.user_dependency import get_current_user_id

router = APIRouter(prefix="/pricing", tags=["Pricing"])

@router.post("/create_package", summary="Create pricing package")
async def create_package(package_data: SZonePackage, user_id: int = Depends(get_current_user_id)):
    return await PackageDAO.add(**package_data.model_dump())


@router.post("/calculate_bulk", response_model=STotalPriceResponse)
async def calculate_bulk(data: List[SBulkPriceRequest]):
    return await PricingService.calculate_bulk_price(data)