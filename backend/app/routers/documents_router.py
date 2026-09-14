"""
IT'S MY AI — Document Intelligence API Router
Implements Section 10:
- File ingestion and parsing endpoints
- Multipart file upload for instant document summarization
- Integration with AI provider cascade
"""

import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.services.document_service import document_service

router = APIRouter(prefix="/api/documents", tags=["Documents"])

DOCS_DIR = settings.STORAGE_DIR / "documents"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

class DocumentAnalyzeRequest(BaseModel):
    file_path: str
    question: Optional[str] = None

@router.get("/supported")
async def get_supported_formats():
    """Returns supported document formats."""
    return {
        "supported_extensions": [".pdf", ".docx", ".doc", ".csv", ".txt", ".json", ".md"],
        "max_size_chars": document_service.max_chars_limit,
        "anti_injection_shield": True
    }

@router.post("/analyze")
async def analyze_document_path(req: DocumentAnalyzeRequest):
    """Analyzes a local file on the user's computer."""
    result = await document_service.analyze_document(req.file_path, req.question)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to analyze document."))
    return result

@router.post("/upload")
async def upload_and_analyze_document(
    file: UploadFile = File(...),
    question: Optional[str] = Form(None)
):
    """Accepts document upload, safely stores in storage/documents, and runs AI analysis."""
    safe_name = Path(file.filename).name
    save_path = DOCS_DIR / safe_name

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    result = await document_service.analyze_document(str(save_path), question)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Document processing failed."))
    return result
