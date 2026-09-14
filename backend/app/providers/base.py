"""
IT'S MY AI — Base AI Provider Interface
Defines the uniform provider abstraction for Gemini, Groq, OpenAI, and Fallbacks.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class AIResponse(BaseModel):
    text: str
    provider: str
    model: str
    latency_ms: int
    intent: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tokens_used: Optional[int] = None
    mode: str = "NORMAL"

class AIProvider(ABC):
    """Abstract interface for all cloud and local AI inference providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g., 'gemini', 'groq', 'openai', 'mock')."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the necessary API key or environment is ready."""
        pass

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        response_mode: str = "NORMAL",
        available_tools: Optional[List[Dict[str, Any]]] = None
    ) -> AIResponse:
        """Generates an AI response, optionally calling registered tools."""
        pass
