"""
IT'S MY AI — AI Chat & Brain Router
Handles /api/ai endpoints: chat completions, provider switching, intent detection.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.app.providers.manager import provider_manager
from backend.app.tools.registry import tool_registry
from backend.app.core.audit import AuditLogger
from backend.app.core.anti_injection import AntiInjectionGuard

router = APIRouter(prefix="/api/ai", tags=["AI Brain"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    response_mode: str = "NORMAL"  # NORMAL, DETAILED, TECHNICAL, ACTION
    confirmed_tool: Optional[str] = None
    confirmed_params: Optional[Dict[str, Any]] = None

class ProviderSwitchRequest(BaseModel):
    provider_name: str

@router.post("/chat")
async def chat_completion(req: ChatRequest):
    """
    Core AI processing pipeline:
    User Input -> Intent Detection -> Tool Resolution -> Permission Check -> Execution / Confirmation -> AI Response
    """
    raw_messages = [{"role": m.role, "content": m.content} for m in req.messages]
    last_user_msg = raw_messages[-1]["content"] if raw_messages else ""

    # Check for potential prompt injection attempts in input
    flagged = AntiInjectionGuard.check_for_injection(last_user_msg)
    if flagged:
        AuditLogger.log_event(
            event_type="security_alert",
            action="Prompt injection pattern detected",
            status="flagged",
            details={"pattern": flagged}
        )

    # 1. If user is explicitly confirming a previous tool call:
    if req.confirmed_tool:
        tool_result = await tool_registry.execute_tool(
            name=req.confirmed_tool,
            parameters=req.confirmed_params or {},
            is_confirmed=True
        )
        return {
            "text": f"Confirmed action '{req.confirmed_tool}' executed successfully.",
            "provider": provider_manager.active_provider_name,
            "model": "system-executor",
            "latency_ms": tool_result.get("duration_ms", 10),
            "tool_result": tool_result,
            "hologram_state": "SUCCESS" if tool_result.get("success") else "ERROR"
        }

    # 2. Query active AI provider
    tools_schema = tool_registry.list_tools()
    ai_resp = await provider_manager.execute_query(
        messages=raw_messages,
        response_mode=req.response_mode,
        available_tools=tools_schema
    )

    # 3. Check if tool calls were triggered
    tool_results = []
    requires_confirmation = False
    confirmation_data = None
    hologram_state = "SPEAKING"

    if ai_resp.tool_calls:
        for tc in ai_resp.tool_calls:
            t_name = tc.get("name")
            t_params = tc.get("parameters", {})
            t_exec = await tool_registry.execute_tool(t_name, t_params, is_confirmed=False)

            if t_exec.get("requires_confirmation"):
                requires_confirmation = True
                confirmation_data = t_exec
                hologram_state = "EXECUTING"
                break
            else:
                tool_results.append(t_exec)

    return {
        "text": ai_resp.text,
        "provider": ai_resp.provider,
        "model": ai_resp.model,
        "latency_ms": ai_resp.latency_ms,
        "tokens_used": ai_resp.tokens_used,
        "mode": ai_resp.mode,
        "intent": ai_resp.intent,
        "tool_calls": ai_resp.tool_calls,
        "tool_results": tool_results,
        "requires_confirmation": requires_confirmation,
        "confirmation_data": confirmation_data,
        "hologram_state": hologram_state
    }

@router.get("/providers")
async def list_providers():
    """Lists available AI providers and current active status."""
    return {
        "active": provider_manager.active_provider_name,
        "providers": provider_manager.list_providers()
    }

@router.post("/providers/switch")
async def switch_provider(req: ProviderSwitchRequest):
    """Switches the active inference provider."""
    success = provider_manager.set_active_provider(req.provider_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Provider '{req.provider_name}' is not recognized.")
    return {"success": True, "active_provider": req.provider_name}
