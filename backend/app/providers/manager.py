"""
IT'S MY AI — Provider Manager & Orchestration Layer
Orchestrates AI inference providers, manages automatic fallback cascade,
and tracks response metrics (latency, token usage, error recovery).
"""

from typing import Dict, List, Any, Optional
from backend.app.providers.base import AIProvider, AIResponse
from backend.app.providers.gemini_provider import GeminiProvider
from backend.app.providers.groq_provider import GroqProvider
from backend.app.providers.openai_provider import OpenAIProvider
from backend.app.providers.mock_provider import MockOfflineProvider
from backend.app.config import settings
from backend.app.core.audit import AuditLogger

SYSTEM_INSTRUCTION = (
    "You are IT'S MY AI, a production-quality personal AI assistant and command center. "
    "Your identity is 'IT'S MY AI'. "
    "You sound: intelligent, calm, concise, helpful, respectful, slightly futuristic, and confident. "
    "Never use excessive robotic phrases. "
    "You operate in harmony with a local Windows desktop environment and respect user security permissions."
)

class ProviderManager:
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {
            "gemini": GeminiProvider(),
            "groq": GroqProvider(),
            "openai": OpenAIProvider(),
            "mock": MockOfflineProvider(),
        }
        self.active_provider_name = settings.DEFAULT_AI_PROVIDER

    def get_active_provider(self) -> AIProvider:
        # If requested provider is configured, use it; otherwise fallback
        provider = self.providers.get(self.active_provider_name)
        if provider and provider.is_configured():
            return provider
        # Try finding first configured cloud provider
        for name in ["gemini", "groq", "openai"]:
            p = self.providers[name]
            if p.is_configured():
                return p
        return self.providers["mock"]

    def set_active_provider(self, name: str) -> bool:
        if name in self.providers:
            self.active_provider_name = name
            AuditLogger.log_event(
                event_type="provider_switch",
                action=f"Switched active provider to {name}",
                status="success",
                details={"new_provider": name}
            )
            return True
        return False

    def list_providers(self) -> List[Dict[str, Any]]:
        result = []
        for name, p in self.providers.items():
            result.append({
                "name": name,
                "is_configured": p.is_configured(),
                "is_active": name == self.active_provider_name,
            })
        return result

    async def execute_query(
        self,
        messages: List[Dict[str, str]],
        response_mode: str = "NORMAL",
        available_tools: Optional[List[Dict[str, Any]]] = None
    ) -> AIResponse:
        """
        Executes query with automatic fallback cascade if the primary provider fails.
        Never crashes when an API fails (Section 32).
        """
        primary = self.get_active_provider()
        try:
            return await primary.generate_response(
                messages=messages,
                system_instruction=SYSTEM_INSTRUCTION,
                response_mode=response_mode,
                available_tools=available_tools
            )
        except Exception as e:
            AuditLogger.log_event(
                event_type="api_failure",
                action=f"Provider {primary.name} failed",
                status="fallback_triggered",
                details={"error": str(e), "primary": primary.name}
            )
            # Graceful degradation to offline fallback
            fallback = self.providers["mock"]
            response = await fallback.generate_response(
                messages=messages,
                system_instruction=SYSTEM_INSTRUCTION,
                response_mode=response_mode,
                available_tools=available_tools
            )
            response.text = (
                f"[Notice: {primary.name.upper()} API unavailable. Degraded to offline fallback.]\n\n"
                f"{response.text}"
            )
            return response

provider_manager = ProviderManager()
