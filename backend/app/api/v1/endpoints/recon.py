"""
Reconnaissance results endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import ReconResult
from app.db.session import get_db

router = APIRouter()


@router.get("/{scan_id}/subdomains")
async def get_subdomains(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get discovered subdomains for a scan
    """
    # TODO: Implement get subdomains
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get subdomains not yet implemented"
    )


@router.get("/{scan_id}/ports")
async def get_ports(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get discovered ports for a scan
    """
    # TODO: Implement get ports
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get ports not yet implemented"
    )


@router.get("/{scan_id}/technologies")
async def get_technologies(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detected technologies for a scan
    """
    # TODO: Implement get technologies
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get technologies not yet implemented"
    )


@router.get("/{scan_id}/endpoints")
async def get_endpoints(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get discovered endpoints for a scan
    """
    # TODO: Implement get endpoints
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get endpoints not yet implemented"
    )


@router.get("/{scan_id}/parameters")
async def get_parameters(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get discovered parameters for a scan
    """
    # TODO: Implement get parameters
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get parameters not yet implemented"
    )


@router.get("/{scan_id}/results", response_model=List[ReconResult])
async def get_all_recon_results(
    scan_id: int,
    recon_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all reconnaissance results for a scan
    """
    # TODO: Implement get all recon results
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get recon results not yet implemented"
    )
