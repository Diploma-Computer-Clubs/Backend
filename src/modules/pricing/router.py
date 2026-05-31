from typing import List

from fastapi import APIRouter, Depends

from src.modules.pricing.dao import PackageDAO
from src.modules.pricing.schemas import SBulkPriceRequest, SZonePackage, SZonePackageGet, SZonePackageUpdate, STotalPriceResponse
from src.modules.pricing.service import PricingService
from src.shared.dependencies.dependencies import RoleChecker

router = APIRouter(prefix="/pricing", tags=["Pricing management"])

@router.get("/", summary="Get club packages (owner)", response_model=List[SZonePackageGet])
async def get_packages(club_id: int, auth: int = Depends(RoleChecker([]))):
    return await PricingService.get_club_packages(club_id)


@router.post("/", summary="Create pricing package (owner)")
async def create_package(package_data: SZonePackage, auth: int = Depends(RoleChecker([]))):
    return await PackageDAO.add(**package_data.model_dump())


@router.patch("/{package_id}", summary="Update pricing package (owner)")
async def update_package(package_id: int, package_data: SZonePackageUpdate, auth: int = Depends(RoleChecker([]))):
    return await PricingService.update_package(package_id, package_data)


@router.delete("/{package_id}", summary="Delete pricing package (owner)")
async def delete_package(package_id: int, auth: int = Depends(RoleChecker([]))):
    return await PricingService.delete_package(package_id)


@router.post("/calculate", response_model=STotalPriceResponse)
async def calculate_bulk(data: List[SBulkPriceRequest]):
    return await PricingService.calculate_bulk_price(data)
