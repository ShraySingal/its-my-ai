"""
IT'S MY AI — Long-Term Memory Router
Complies with Section 8: Memory retrieval, controlled storage, and deletion.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from backend.app.services.memory_service import memory_service

router = APIRouter(prefix="/api/memory", tags=["Long-Term Memory"])

class StoreMemoryRequest(BaseModel):
    content: str
    category: str = "fact"
    tags: Optional[List[str]] = None

@router.get("")
async def get_memories(q: str = ""):
    """Searches or lists all memories."""
    return {"memories": memory_service.search_memories(q)}

@router.post("")
async def store_memory(req: StoreMemoryRequest):
    """Explicitly stores a new memory item."""
    return memory_service.store_memory(content=req.content, category=req.category, tags=req.tags)

@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """Deletes a specific memory entry."""
    success = memory_service.delete_memory(memory_id)
    return {"success": success, "memory_id": memory_id}

@router.delete("")
async def clear_memories(confirmed: bool = False):
    """Wipes all memories if confirmed."""
    if not confirmed:
        return {"success": False, "requires_confirmation": True, "message": "Confirm memory wipe."}
    count = memory_service.clear_all_memories()
    return {"success": True, "deleted_count": count}
