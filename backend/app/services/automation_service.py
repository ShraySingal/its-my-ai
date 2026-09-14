"""
IT'S MY AI — Automation Routines Service
Implements Section 30: Multi-step personal workflows and routines.
"""

from typing import List, Dict, Any
from backend.app.core.audit import AuditLogger

class AutomationService:
    def __init__(self):
        self._routines = {
            "coding_routine": {
                "name": "Start My Coding Routine",
                "trigger": "start my coding routine",
                "description": "Sets up development environment, opens docs, and activates holographic dashboard.",
                "requires_confirmation": False,
                "steps": [
                    {"action": "open_application", "target": "VS Code", "status": "pending"},
                    {"action": "open_browser_url", "target": "https://github.com", "status": "pending"},
                    {"action": "open_browser_url", "target": "https://docs.python.org", "status": "pending"},
                    {"action": "activate_hologram_mode", "target": "dashboard", "status": "pending"},
                ]
            },
            "good_night": {
                "name": "Good Night Routine",
                "trigger": "good night",
                "description": "Saves state, silences notifications, dims display, and transitions AI to sleep state.",
                "requires_confirmation": True,
                "steps": [
                    {"action": "save_session_state", "target": "workspace", "status": "pending"},
                    {"action": "mute_system_audio", "target": "local_machine", "status": "pending"},
                    {"action": "switch_hologram_state", "target": "SLEEP", "status": "pending"},
                    {"action": "lock_workstation", "target": "windows", "status": "pending"},
                ]
            }
        }

    def list_routines(self) -> List[Dict[str, Any]]:
        return [{"id": k, **v} for k, v in self._routines.items()]

    def execute_routine(self, routine_id: str, is_confirmed: bool = False) -> Dict[str, Any]:
        routine = self._routines.get(routine_id)
        if not routine:
            return {"success": False, "message": f"Routine '{routine_id}' not found."}

        if routine["requires_confirmation"] and not is_confirmed:
            return {
                "success": False,
                "requires_confirmation": True,
                "routine_id": routine_id,
                "message": f"Confirmation required to run disruptive routine '{routine['name']}'."
            }

        executed_steps = []
        for step in routine["steps"]:
            executed_steps.append({
                "action": step["action"],
                "target": step["target"],
                "status": "completed"
            })

        AuditLogger.log_event(
            event_type="routine_execution",
            action=f"Executed routine '{routine['name']}'",
            status="success",
            permission_level=3 if routine["requires_confirmation"] else 1,
            details={"routine_id": routine_id, "steps_count": len(executed_steps)}
        )

        return {
            "success": True,
            "routine_id": routine_id,
            "name": routine["name"],
            "steps": executed_steps,
            "message": f"Successfully executed '{routine['name']}' with {len(executed_steps)} steps."
        }

automation_service = AutomationService()
