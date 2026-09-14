"""
IT'S MY AI — Multi-Device Router
Complies with Sections 19 & 20: Paired device directory, heartbeats, and cross-device actions.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.app.services.device_service import device_service

router = APIRouter(prefix="/api/devices", tags=["Multi-Device"])

class HeartbeatRequest(BaseModel):
    device_id: str
    battery: Optional[int] = None
    status: str = "ONLINE"

class SendFileRequest(BaseModel):
    target_device: str
    file_name: str

@router.get("")
async def list_devices():
    """Lists all paired devices and connection statuses."""
    return {"devices": device_service.list_devices()}

@router.post("/heartbeat")
async def device_heartbeat(req: HeartbeatRequest):
    """Updates device heartbeat, online status, and battery."""
    success = device_service.update_heartbeat(req.device_id, req.battery, req.status)
    return {"success": success}

@router.post("/send-file")
async def send_file_to_device(req: SendFileRequest):
    """Pipeline: Laptop -> Cloud Storage -> Mobile Agent -> Target Device."""
    return device_service.send_file_to_device(req.target_device, req.file_name)
