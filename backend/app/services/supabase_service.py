"""
IT'S MY AI — Supabase Cloud Database & Storage Client
Implements Sections 8, 9, and 39:
- Cloud PostgreSQL memory, device, and task synchronization
- Cloud object storage for documents, images, backups, and hologram assets
- Zero-overhead async HTTP client using httpx (no heavy SDK dependencies)
- Graceful offline fallback: if unconfigured, safely degrades to local storage
"""

import httpx
from typing import Dict, Any, List, Optional
from backend.app.config import settings
from backend.app.core.audit import AuditLogger

class SupabaseService:
    def __init__(self):
        self.url = settings.SUPABASE_URL.rstrip("/") if settings.SUPABASE_URL else ""
        self.key = settings.SUPABASE_KEY if settings.SUPABASE_KEY else ""

    def is_configured(self) -> bool:
        """Returns True if valid Supabase URL and key are provided."""
        return bool(self.url and self.key and not self.url.startswith("https://your-project"))

    def _get_headers(self) -> Dict[str, str]:
        return {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    async def sync_memory(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Uploads or updates a memory record in Supabase cloud database."""
        if not self.is_configured():
            return {"success": False, "synced": False, "reason": "Supabase not configured. Using local memories.json."}

        endpoint = f"{self.url}/rest/v1/memories"
        payload = {
            "id": memory_data.get("id"),
            "content": memory_data.get("content"),
            "category": memory_data.get("category", "fact"),
            "tags": memory_data.get("tags", []),
            "created_at": memory_data.get("created_at")
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(endpoint, json=payload, headers=self._get_headers())
                if res.status_code in (200, 201):
                    return {"success": True, "synced": True, "cloud_data": res.json()}
                return {"success": False, "synced": False, "status_code": res.status_code, "error": res.text}
        except Exception as e:
            return {"success": False, "synced": False, "error": str(e)}

    async def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Deletes a memory record from Supabase cloud database."""
        if not self.is_configured():
            return {"success": True, "synced": False, "reason": "Supabase not configured."}

        endpoint = f"{self.url}/rest/v1/memories?id=eq.{memory_id}"
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.delete(endpoint, headers=self._get_headers())
                return {"success": res.status_code in (200, 204), "status_code": res.status_code}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def sync_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Syncs device heartbeat telemetry to Supabase cloud registry."""
        if not self.is_configured():
            return {"success": True, "synced": False, "reason": "Supabase not configured. Using local devices.json."}

        endpoint = f"{self.url}/rest/v1/devices"
        headers = self._get_headers()
        headers["Prefer"] = "resolution=merge-duplicates"

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(endpoint, json=device_data, headers=headers)
                return {"success": res.status_code in (200, 201, 204), "synced": True}
        except Exception as e:
            return {"success": False, "synced": False, "error": str(e)}

    async def upload_file(
        self,
        bucket: str,
        remote_filename: str,
        file_bytes: bytes,
        mime_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        """Uploads a file to Supabase Cloud Storage bucket (documents, images, backups, etc.)."""
        if not self.is_configured():
            return {"success": False, "error": "Supabase storage is not configured in .env."}

        endpoint = f"{self.url}/storage/v1/object/{bucket}/{remote_filename}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": mime_type,
            "x-upsert": "true"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(endpoint, content=file_bytes, headers=headers)
                if res.status_code in (200, 201):
                    public_url = f"{self.url}/storage/v1/object/public/{bucket}/{remote_filename}"
                    return {"success": True, "bucket": bucket, "path": remote_filename, "url": public_url}
                return {"success": False, "error": res.text, "status_code": res.status_code}
        except Exception as e:
            return {"success": False, "error": str(e)}

supabase_service = SupabaseService()
