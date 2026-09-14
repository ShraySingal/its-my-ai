"""
IT'S MY AI — Long-Term Memory Service
Implements controlled, transparent memory storage & retrieval (Section 8).
Supports user preferences, facts, project states, and explicit memory deletion.
"""

import json
import time
import uuid
import httpx
from typing import List, Dict, Any, Optional
from backend.app.config import settings
from backend.app.core.audit import AuditLogger

class MemoryService:
    def __init__(self):
        self._load_memories()

    def _load_memories(self):
        if settings.MEMORIES_FILE.exists():
            try:
                with open(settings.MEMORIES_FILE, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {"memories": []}
        else:
            self._data = {
                "memories": [
                    {
                        "id": str(uuid.uuid4()),
                        "category": "preference",
                        "content": "User prefers futuristic dark HUD aesthetic and calm conversational tone.",
                        "created_at": "2026-09-08T00:00:00Z",
                        "tags": ["theme", "ui", "preference"]
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "category": "system",
                        "content": "Host hardware constraint: 4 GB RAM Intel Core i5-1235U.",
                        "created_at": "2026-09-08T00:00:00Z",
                        "tags": ["hardware", "constraint"]
                    }
                ]
            }
            self._save_memories()

    def _save_memories(self):
        try:
            with open(settings.MEMORIES_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            print(f"Error saving memories: {e}")

    def _sync_to_supabase(self, entry: Dict[str, Any]):
        """Asynchronously or best-effort pushes a memory to Supabase cloud."""
        if not (settings.SUPABASE_URL and settings.SUPABASE_KEY):
            return
        try:
            url = f"{settings.SUPABASE_URL}/rest/v1/memories"
            headers = {
                "apikey": settings.SUPABASE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            }
            with httpx.Client(timeout=3.0) as client:
                client.post(url, headers=headers, json=entry)
        except Exception:
            pass

    def _delete_from_supabase(self, memory_id: str):
        """Asynchronously or best-effort deletes a memory from Supabase cloud."""
        if not (settings.SUPABASE_URL and settings.SUPABASE_KEY):
            return
        try:
            url = f"{settings.SUPABASE_URL}/rest/v1/memories?id=eq.{memory_id}"
            headers = {
                "apikey": settings.SUPABASE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_KEY}"
            }
            with httpx.Client(timeout=3.0) as client:
                client.delete(url, headers=headers)
        except Exception:
            pass

    def store_memory(self, content: str, category: str = "fact", tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Explicitly stores an item in long-term memory."""
        mem_id = str(uuid.uuid4())
        entry = {
            "id": mem_id,
            "category": category,
            "content": content,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tags": tags or ["user_input"]
        }
        self._data["memories"].append(entry)
        self._save_memories()

        # Cloud sync (best-effort, non-blocking)
        self._sync_to_supabase(entry)

        AuditLogger.log_event(
            event_type="memory_event",
            action="Stored new memory",
            status="success",
            details={"memory_id": mem_id, "category": category, "cloud_synced": bool(settings.SUPABASE_URL)}
        )
        return entry

    def search_memories(self, query: str = "") -> List[Dict[str, Any]]:
        """Searches memories by keyword or returns all if empty."""
        q = query.lower().strip()
        if not q:
            return self._data.get("memories", [])
        return [
            m for m in self._data.get("memories", [])
            if q in m["content"].lower() or any(q in t.lower() for t in m.get("tags", []))
        ]

    def delete_memory(self, memory_id: str) -> bool:
        """Deletes a specific memory entry."""
        initial_len = len(self._data.get("memories", []))
        self._data["memories"] = [m for m in self._data.get("memories", []) if m["id"] != memory_id]
        if len(self._data["memories"]) < initial_len:
            self._save_memories()
            self._delete_from_supabase(memory_id)
            AuditLogger.log_event(
                event_type="memory_event",
                action="Deleted memory entry",
                status="success",
                details={"memory_id": memory_id}
            )
            return True
        return False

    def clear_all_memories(self) -> int:
        """Wipes all stored memories (Requires confirmation in caller)."""
        count = len(self._data.get("memories", []))
        self._data["memories"] = []
        self._save_memories()
        AuditLogger.log_event(
            event_type="memory_event",
            action="Wiped all stored memories",
            status="success",
            permission_level=4,
            details={"deleted_count": count}
        )
        return count

memory_service = MemoryService()
