"""
IT'S MY AI — System & Audit Router
Provides real-time host hardware telemetry and structured audit event stream.
"""

from fastapi import APIRouter
from backend.app.services.system_service import system_service
from backend.app.core.audit import AuditLogger

router = APIRouter(prefix="/api/system", tags=["System Telemetry"])

@router.get("/status")
async def get_system_status():
    """Returns live hardware metrics for CPU, 4 GB RAM, Disk, Battery, and Network."""
    return system_service.get_telemetry()

@router.get("/audit")
async def get_audit_logs(limit: int = 50):
    """Returns recent structured security audit events."""
    return {
        "count": limit,
        "events": AuditLogger.get_recent_events(limit)
    }
