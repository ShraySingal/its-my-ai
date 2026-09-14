"""
IT'S MY AI — Tools API Router
Allows listing registered tools and manually executing actions with confirmation support.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.app.tools.registry import tool_registry

router = APIRouter(prefix="/api/tools", tags=["Tools Registry"])

class ToolExecuteRequest(BaseModel):
    name: str
    parameters: Dict[str, Any] = {}
    is_confirmed: bool = False

@router.get("/list")
async def list_tools():
    """Lists all registered tools, descriptions, parameter schemas, and permission levels."""
    return {"tools": tool_registry.list_tools()}

@router.post("/execute")
async def execute_tool(req: ToolExecuteRequest):
    """Executes a tool with 4-level permission validation and confirmation check."""
    return await tool_registry.execute_tool(
        name=req.name,
        parameters=req.parameters,
        is_confirmed=req.is_confirmed
    )
