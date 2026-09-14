"""
IT'S MY AI — To-Do & Task Management Service
Provides persistent, local task management with categorization, priority levels,
and comprehensive audit logging for the personal command center.
"""

import json
import time
import uuid
from typing import List, Dict, Any, Optional
from backend.app.config import settings
from backend.app.core.audit import AuditLogger

class TodoService:
    def __init__(self):
        self._load_todos()

    def _load_todos(self):
        if settings.TODOS_FILE.exists():
            try:
                with open(settings.TODOS_FILE, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {"todos": []}
        else:
            self._data = {
                "todos": [
                    {
                        "id": "todo_1",
                        "title": "Review Security Guardian audit log & network score",
                        "category": "security",
                        "priority": "high",
                        "completed": false,
                        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "completed_at": None
                    }
                ]
            }
            self._save_todos()

    def _save_todos(self):
        try:
            with open(settings.TODOS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            print(f"Error saving todos: {e}")

    def list_todos(
        self,
        category: Optional[str] = None,
        completed: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries todos with optional filters for category, completion state, and search query."""
        results = self._data.get("todos", [])
        
        if category and category.lower() != "all":
            results = [t for t in results if t.get("category", "").lower() == category.lower()]
            
        if completed is not None:
            results = [t for t in results if t.get("completed") is completed]
            
        if search:
            q = search.lower().strip()
            results = [t for t in results if q in t.get("title", "").lower() or q in t.get("category", "").lower()]
            
        return results

    def add_todo(
        self,
        title: str,
        category: str = "general",
        priority: str = "medium",
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates and stores a new to-do task."""
        todo_id = f"todo_{uuid.uuid4().hex[:8]}"
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        item = {
            "id": todo_id,
            "title": title.strip(),
            "category": category.strip().lower() or "general",
            "priority": priority.strip().lower() if priority in ["low", "medium", "high", "urgent"] else "medium",
            "completed": False,
            "due_date": due_date,
            "created_at": now,
            "completed_at": None
        }
        
        self._data["todos"].insert(0, item)
        self._save_todos()

        AuditLogger.log_event(
            event_type="todo_event",
            action="Created task",
            status="success",
            details={"todo_id": todo_id, "title": title, "priority": priority, "category": category}
        )
        return item

    def toggle_todo(self, todo_id: str, completed: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        """Toggles or sets the completion state of a task."""
        for item in self._data.get("todos", []):
            if item["id"] == todo_id:
                new_state = (not item["completed"]) if completed is None else completed
                item["completed"] = new_state
                item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) if new_state else None
                self._save_todos()

                AuditLogger.log_event(
                    event_type="todo_event",
                    action=f"Marked task {'completed' if new_state else 'pending'}",
                    status="success",
                    details={"todo_id": todo_id, "title": item["title"], "completed": new_state}
                )
                return item
        return None

    def update_todo(
        self,
        todo_id: str,
        title: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Updates fields of an existing task."""
        for item in self._data.get("todos", []):
            if item["id"] == todo_id:
                if title is not None:
                    item["title"] = title.strip()
                if category is not None:
                    item["category"] = category.strip().lower()
                if priority is not None and priority in ["low", "medium", "high", "urgent"]:
                    item["priority"] = priority.strip().lower()
                    
                self._save_todos()
                AuditLogger.log_event(
                    event_type="todo_event",
                    action="Updated task",
                    status="success",
                    details={"todo_id": todo_id, "title": item["title"]}
                )
                return item
        return None

    def delete_todo(self, todo_id: str) -> bool:
        """Deletes a task by ID."""
        initial_count = len(self._data.get("todos", []))
        self._data["todos"] = [t for t in self._data.get("todos", []) if t["id"] != todo_id]
        
        if len(self._data["todos"]) < initial_count:
            self._save_todos()
            AuditLogger.log_event(
                event_type="todo_event",
                action="Deleted task",
                status="success",
                details={"todo_id": todo_id}
            )
            return True
        return False

    def clear_completed_todos(self) -> int:
        """Removes all completed tasks."""
        initial_count = len(self._data.get("todos", []))
        self._data["todos"] = [t for t in self._data.get("todos", []) if not t.get("completed")]
        removed = initial_count - len(self._data["todos"])
        
        if removed > 0:
            self._save_todos()
            AuditLogger.log_event(
                event_type="todo_event",
                action="Cleared completed tasks",
                status="success",
                details={"count": removed}
            )
        return removed

todo_service = TodoService()
