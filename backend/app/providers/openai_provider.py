"""
IT'S MY AI — OpenAI Provider
Connects to OpenAI API endpoints (GPT-4o, GPT-4o-mini).
"""

import time
import httpx
from typing import List, Dict, Any, Optional
from backend.app.providers.base import AIProvider, AIResponse
from backend.app.config import settings

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = "gpt-4o-mini"

    @property
    def name(self) -> str:
        return "openai"

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        response_mode: str = "NORMAL",
        available_tools: Optional[List[Dict[str, Any]]] = None
    ) -> AIResponse:
        start_time = time.time()
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        chat_messages = [{"role": "system", "content": f"{system_instruction}\nResponse Mode: {response_mode}"}]
        chat_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": chat_messages,
            "temperature": 0.6,
            "max_tokens": 1024,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        latency = int((time.time() - start_time) * 1000)
        text = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)

        return AIResponse(
            text=text.strip(),
            provider="openai",
            model=self.model,
            latency_ms=latency,
            tokens_used=tokens,
            mode=response_mode
        )

    async def analyze_image(self, image_base64: str, prompt: str = "Analyze this screenshot.") -> str:
        """Analyzes an image using OpenAI vision capabilities."""
        if not self.is_configured():
            raise ValueError("OpenAI API key is not configured.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }],
            "max_tokens": 1024
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        return data["choices"][0]["message"]["content"].strip()

