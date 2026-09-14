"""
IT'S MY AI — Automation Routines Router
Complies with Section 30: Personal automation workflows.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services.automation_service import automation_service

router = APIRouter(prefix="/api/automation", tags=["Automation"])

class RoutineExecuteRequest(BaseModel):
    routine_id: str
    is_confirmed: bool = False

@router.get("/routines")
async def list_routines():
    """Lists available automation routines."""
    return {"routines": automation_service.list_routines()}

@router.post("/routines/execute")
async def execute_routine(req: RoutineExecuteRequest):
    """Executes a routine with confirmation protection."""
    return automation_service.execute_routine(req.routine_id, is_confirmed=req.is_confirmed)
