"""
IT'S MY AI — Groq Cloud AI Provider
Connects to Groq ultra-fast inference API with OpenAI-compatible payload.
"""

import time
import httpx
from typing import List, Dict, Any, Optional
from backend.app.providers.base import AIProvider, AIResponse
from backend.app.config import settings

class GroqProvider(AIProvider):
    CANDIDATE_MODELS = [
        "qwen/qwen3.8-27b",
        "groq/compound-mini",
        "groq/compound",
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile"
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = "qwen/qwen3.8-27b"

    @property
    def name(self) -> str:
        return "groq"

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
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        chat_messages = [{"role": "system", "content": f"{system_instruction}\nResponse Mode: {response_mode}"}]
        chat_messages.extend(messages)

        # Build OpenAI compatible tools schema if provided
        tools_payload = None
        if available_tools:
            tools_payload = []
            for t in available_tools:
                tools_payload.append({
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t.get("description", ""),
                        "parameters": {
                            "type": "object",
                            "properties": t.get("parameters", {}),
                        }
                    }
                })

        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "").strip()
                break
        q_lower = last_user_msg.lower()

        last_err = None
        for candidate_model in [self.model] + [m for m in self.CANDIDATE_MODELS if m != self.model]:
            payload = {
                "model": candidate_model,
                "messages": chat_messages,
                "temperature": 0.5,
                "max_tokens": 1024,
            }
            if tools_payload and "compound" not in candidate_model:
                payload["tools"] = tools_payload

            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        msg = data["choices"][0]["message"]
                        text = msg.get("content") or ""
                        # If model returned thinking tags, strip them cleanly
                        if "<think>" in text and "</think>" in text:
                            text = text.split("</think>")[-1].strip()

                        # Parse native tool calls
                        tool_calls = None
                        if msg.get("tool_calls"):
                            tool_calls = []
                            import json
                            for tc in msg["tool_calls"]:
                                try:
                                    args = json.loads(tc["function"].get("arguments", "{}"))
                                except Exception:
                                    args = {}
                                tool_calls.append({
                                    "name": tc["function"]["name"],
                                    "parameters": args
                                })

                        # Fallback heuristic tool mapping for desktop commands
                        if not tool_calls:
                            if "how much ram" in q_lower or ("ram" in q_lower and ("usage" in q_lower or "do i have" in q_lower or "system" in q_lower)):
                                tool_calls = [{"name": "get_system_status", "parameters": {}}]
                            elif "weather" in q_lower:
                                tool_calls = [{"name": "get_weather", "parameters": {"location": "current"}}]
                            elif "screenshot" in q_lower or "analyze screen" in q_lower:
                                tool_calls = [{"name": "analyze_screen", "parameters": {"question": last_user_msg}}]

                        self.model = candidate_model
                        latency = int((time.time() - start_time) * 1000)
                        tokens = data.get("usage", {}).get("total_tokens", 0)
                        return AIResponse(
                            text=text.strip() if text else "Processing your system command.",
                            provider="groq",
                            model=self.model,
                            latency_ms=latency,
                            tokens_used=tokens,
                            mode=response_mode,
                            tool_calls=tool_calls
                        )
                    else:
                        last_err = f"Status {resp.status_code}: {resp.text}"
            except Exception as e:
                last_err = str(e)
                continue

        raise RuntimeError(f"Groq inference failed on all candidate models: {last_err}")


