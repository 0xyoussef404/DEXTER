"""
API v1 Router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import scans, targets, findings, recon, auth, users

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(targets.router, prefix="/targets", tags=["Targets"])
api_router.include_router(scans.router, prefix="/scans", tags=["Scans"])
api_router.include_router(findings.router, prefix="/findings", tags=["Findings"])
api_router.include_router(recon.router, prefix="/recon", tags=["Reconnaissance"])
