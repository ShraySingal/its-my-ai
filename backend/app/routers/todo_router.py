"""
IT'S MY AI — To-Do & Task Management Router
REST endpoints for managing user tasks, prioritization, categories, and completion states.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.app.services.todo_service import todo_service

router = APIRouter(prefix="/api/todos", tags=["To-Do & Tasks"])

class CreateTodoRequest(BaseModel):
    title: str
    category: str = "general"
    priority: str = "medium"  # low, medium, high, urgent
    due_date: Optional[str] = None

class UpdateTodoRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None

class ToggleTodoRequest(BaseModel):
    completed: Optional[bool] = None

@router.get("")
async def list_todos(
    category: Optional[str] = None,
    completed: Optional[bool] = None,
    search: Optional[str] = None
):
    """Retrieves list of tasks matching optional filters."""
    items = todo_service.list_todos(category=category, completed=completed, search=search)
    return {
        "todos": items,
        "count": len(items)
    }

@router.post("")
async def create_todo(req: CreateTodoRequest):
    """Adds a new task to the to-do list."""
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    item = todo_service.add_todo(
        title=req.title,
        category=req.category,
        priority=req.priority,
        due_date=req.due_date
    )
    return {"success": True, "todo": item}

@router.patch("/{todo_id}/toggle")
async def toggle_todo(todo_id: str, req: Optional[ToggleTodoRequest] = None):
    """Toggles or sets task completion state."""
    target_completed = req.completed if req else None
    item = todo_service.toggle_todo(todo_id, completed=target_completed)
    if not item:
        raise HTTPException(status_code=404, detail=f"Task '{todo_id}' not found.")
    return {"success": True, "todo": item}

@router.put("/{todo_id}")
async def update_todo(todo_id: str, req: UpdateTodoRequest):
    """Updates title, priority, or category of a task."""
    item = todo_service.update_todo(
        todo_id,
        title=req.title,
        category=req.category,
        priority=req.priority
    )
    if not item:
        raise HTTPException(status_code=404, detail=f"Task '{todo_id}' not found.")
    return {"success": True, "todo": item}

@router.delete("/completed/clear")
async def clear_completed_todos():
    """Removes all completed tasks from storage."""
    deleted_count = todo_service.clear_completed_todos()
    return {"success": True, "deleted_count": deleted_count}

@router.delete("/{todo_id}")
async def delete_todo(todo_id: str):
    """Deletes a specific task."""
    deleted = todo_service.delete_todo(todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task '{todo_id}' not found.")
    return {"success": True, "todo_id": todo_id}
