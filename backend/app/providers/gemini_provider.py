"""
IT'S MY AI — Google Gemini AI Provider
Connects to Gemini API via lightweight HTTP client with no heavy SDK overhead.
"""

import time
import httpx
from typing import List, Dict, Any, Optional
from backend.app.providers.base import AIProvider, AIResponse
from backend.app.config import settings

class GeminiProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = "gemini-2.0-flash"

    @property
    def name(self) -> str:
        return "gemini"

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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        # Format contents for Gemini
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": f"{system_instruction}\nCurrent response mode: {response_mode}."}]
            },
            "generationConfig": {
                "temperature": 0.4 if response_mode == "TECHNICAL" else 0.7,
                "maxOutputTokens": 1024,
            }
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency = int((time.time() - start_time) * 1000)
        try:
            candidate = data["candidates"][0]
            text = candidate["content"]["parts"][0]["text"]
            token_count = data.get("usageMetadata", {}).get("totalTokenCount", 0)
        except (KeyError, IndexError):
            text = "I received a response from Gemini, but could not parse the content."
            token_count = 0

        return AIResponse(
            text=text.strip(),
            provider="gemini",
            model=self.model,
            latency_ms=latency,
            tokens_used=token_count,
            mode=response_mode
        )

    async def analyze_image(self, image_base64: str, prompt: str = "Analyze this screenshot.") -> str:
        """Analyzes an image using Gemini 2.0 Flash multimodal vision capabilities."""
        if not self.is_configured():
            raise ValueError("Gemini API key is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": "image/png",
                            "data": image_base64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1024
            }
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError):
            return "Vision analysis completed, but response content was empty."

