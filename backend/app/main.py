"""
IT'S MY AI — Master Application Entrypoint
FastAPI application aggregating all modular routers, mounting holographic UI, and managing lifecycle.
"""

import sys
import os
from pathlib import Path

sys.dont_write_bytecode = True

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.routers.ai_router import router as ai_router
from backend.app.routers.system_router import router as system_router
from backend.app.routers.tools_router import router as tools_router
from backend.app.routers.memory_router import router as memory_router
from backend.app.routers.devices_router import router as devices_router
from backend.app.routers.security_router import router as security_router
from backend.app.routers.automation_router import router as automation_router
from backend.app.routers.ws_router import router as ws_router
from backend.app.routers.todo_router import router as todo_router
from backend.app.routers.vision_router import router as vision_router
from backend.app.routers.documents_router import router as documents_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Personal Cloud AI Command Center optimized for low-resource Windows environments."
)

# Enable CORS for local client and mobile companion access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(ai_router)
app.include_router(system_router)
app.include_router(tools_router)
app.include_router(memory_router)
app.include_router(todo_router)
app.include_router(vision_router)
app.include_router(documents_router)
app.include_router(devices_router)
app.include_router(security_router)
app.include_router(automation_router)
app.include_router(ws_router)

# Mount Frontend Static Directory
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    if (FRONTEND_DIR / "css").exists():
        app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    if (FRONTEND_DIR / "js").exists():
        app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

@app.get("/")
async def serve_index():
    """Serves the main holographic command center interface."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "IT'S MY AI backend online. Frontend index.html not yet mounted."}

@app.get("/manifest.json")
async def serve_manifest():
    """Serves the Web App Manifest for mobile installation."""
    manifest_path = FRONTEND_DIR / "manifest.json"
    if manifest_path.exists():
        return FileResponse(str(manifest_path), media_type="application/manifest+json")
    return {"name": "IT'S MY AI"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "provider": settings.DEFAULT_AI_PROVIDER
    }
