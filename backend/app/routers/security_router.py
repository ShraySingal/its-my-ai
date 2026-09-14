"""
IT'S MY AI — Security Guardian & Network Router
Complies with Sections 21, 22, 23: Defensive audit and authorized network radar data.
"""

from fastapi import APIRouter
from backend.app.services.security_guardian import security_guardian

router = APIRouter(prefix="/api/security", tags=["Security Guardian"])

@router.get("/scan")
async def run_security_scan():
    """Runs Security Guardian defensive checks, open port test, and security score."""
    return security_guardian.run_system_security_check()

@router.get("/network")
async def scan_network():
    """Performs authorized subnet discovery for the 3D Holographic Network Radar."""
    return security_guardian.scan_authorized_network()
