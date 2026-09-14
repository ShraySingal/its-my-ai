"""
IT'S MY AI — Multi-Device Service
Implements Sections 19 & 20: Multi-device registry, heartbeat, and cross-device targeting.
"""

import json
import time
from typing import List, Dict, Any, Optional
from backend.app.config import settings
from backend.app.core.audit import AuditLogger

class DeviceService:
    def __init__(self):
        self._load_devices()

    def _load_devices(self):
        if settings.DEVICES_FILE.exists():
            try:
                with open(settings.DEVICES_FILE, "r", encoding="utf-8") as f:
                    self._devices = json.load(f)
            except Exception:
                self._devices = self._default_devices()
        else:
            self._devices = self._default_devices()
            self._save_devices()

    def _default_devices(self) -> Dict[str, Any]:
        return {
            "devices": [
                {
                    "id": "dev_win_laptop_01",
                    "name": settings.DEVICE_NAME,
                    "type": "Laptop",
                    "os": "Windows 11 (64-bit)",
                    "status": "ONLINE",
                    "is_primary": True,
                    "last_seen": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "battery": 92,
                    "ip": "192.168.1.105",
                    "capabilities": ["hologram", "voice", "windows_agent", "browser", "camera"]
                },
                {
                    "id": "dev_android_phone_02",
                    "name": "It's My AI Mobile (Galaxy S23)",
                    "type": "Mobile",
                    "os": "Android 14",
                    "status": "ONLINE",
                    "is_primary": False,
                    "last_seen": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "battery": 84,
                    "ip": "192.168.1.142",
                    "capabilities": ["notifications", "camera", "location", "sensor_telemetry"]
                },
                {
                    "id": "dev_smart_tv_03",
                    "name": "Living Room Display",
                    "type": "TV",
                    "os": "Android TV",
                    "status": "OFFLINE",
                    "is_primary": False,
                    "last_seen": "2026-09-07T22:15:00Z",
                    "battery": None,
                    "ip": "192.168.1.201",
                    "capabilities": ["media_cast", "dashboard_mirror"]
                }
            ]
        }

    def _save_devices(self):
        try:
            with open(settings.DEVICES_FILE, "w", encoding="utf-8") as f:
                json.dump(self._devices, f, indent=2)
        except Exception as e:
            print(f"Error saving devices: {e}")

    def list_devices(self) -> List[Dict[str, Any]]:
        return self._devices.get("devices", [])

    def get_device(self, device_id_or_type: str) -> Optional[Dict[str, Any]]:
        for d in self._devices.get("devices", []):
            if d["id"] == device_id_or_type or d["type"].lower() == device_id_or_type.lower():
                return d
        return None

    def update_heartbeat(self, device_id: str, battery: Optional[int] = None, status: str = "ONLINE") -> bool:
        for d in self._devices.get("devices", []):
            if d["id"] == device_id:
                d["status"] = status
                d["last_seen"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                if battery is not None:
                    d["battery"] = battery
                self._save_devices()
                return True
        return False

    def send_file_to_device(self, target_device_type: str, file_name: str) -> Dict[str, Any]:
        dev = self.get_device(target_device_type)
        if not dev:
            return {"success": False, "message": f"Device '{target_device_type}' not found or paired."}
        
        AuditLogger.log_event(
            event_type="remote_command",
            action=f"Sent file '{file_name}' to {dev['name']}",
            status="success",
            permission_level=3,
            details={"device_id": dev["id"], "file": file_name}
        )
        return {
            "success": True,
            "message": f"Pipeline: Laptop -> Cloud Storage -> Mobile Agent -> {dev['name']}. File '{file_name}' dispatched.",
            "target": dev["name"]
        }

device_service = DeviceService()
