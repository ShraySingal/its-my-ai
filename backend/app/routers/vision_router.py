"""
IT'S MY AI — Vision & Screen Analysis Router
Provides endpoints to inspect visual telemetry, capture screenshots, and query AI vision models.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.app.services.vision_service import vision_service

router = APIRouter(prefix="/api/vision", tags=["Vision & Screen Intelligence"])

class AnalyzeScreenRequest(BaseModel):
    question: Optional[str] = "What is on my screen right now?"

@router.get("/context")
async def get_window_context():
    """Returns the current active foreground window and process name."""
    return vision_service.get_active_window_context()

@router.get("/screenshot")
async def get_screenshot(fresh: bool = Query(False, description="Capture a fresh screenshot")):
    """Serves the latest desktop screenshot image file."""
    if fresh:
        vision_service.capture_screenshot()
        
    path = vision_service.latest_screenshot_path
    if not path.exists():
        vision_service.capture_screenshot()
        
    if path.exists():
        return FileResponse(str(path), media_type="image/png", filename="latest_screenshot.png")
    raise HTTPException(status_code=404, detail="Screenshot not available.")

@router.post("/analyze")
async def analyze_screen(req: AnalyzeScreenRequest):
    """Captures the current desktop screen and runs multimodal vision analysis."""
    result = await vision_service.analyze_screen(question=req.question or "What is on my screen right now?")
    return result
