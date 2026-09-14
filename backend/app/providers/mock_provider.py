"""
IT'S MY AI — Offline Intelligent Fallback Provider
Operates when internet is unavailable or cloud API keys are absent.
Complies with Sections 32, 33, 36, and 47.
Provides fast, zero-RAM-overhead intent parsing and natural conversational synthesis.
"""

import time
import re
from typing import List, Dict, Any, Optional
from backend.app.providers.base import AIProvider, AIResponse

class MockOfflineProvider(AIProvider):
    @property
    def name(self) -> str:
        return "mock"

    def is_configured(self) -> bool:
        return True  # Always available as guaranteed fallback

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        response_mode: str = "NORMAL",
        available_tools: Optional[List[Dict[str, Any]]] = None
    ) -> AIResponse:
        start_time = time.time()
        last_user_msg = ""
        for m in reversed(messages):
            if m["role"] == "user":
                last_user_msg = m["content"].strip()
                break

        query = last_user_msg.lower()
        # Clean wake phrase if present
        clean_query = re.sub(r"^(hey\s+)?it'?s\s+my\s+ai[,:\s]*", "", query).strip()

        # Intent resolution & tool mapping
        tool_calls = []
        response_text = ""
        intent = "general_conversation"

        if "how much ram" in clean_query or ("ram" in clean_query and ("usage" in clean_query or "do i have" in clean_query)) or "check my laptop" in clean_query or "check laptop" in clean_query:
            intent = "system_telemetry"
            tool_calls.append({"name": "get_system_status", "parameters": {}})
            response_text = "Checking system memory, CPU telemetry, and hardware performance now."

        elif "check my calendar" in clean_query or "show calendar" in clean_query or "my calendar" in clean_query:
            intent = "calendar_events"
            tool_calls.append({"name": "get_calendar_events", "parameters": {}})
            response_text = "Retrieving scheduled appointments and calendar events."

        elif "summarize my emails" in clean_query or "read my emails" in clean_query or "check emails" in clean_query:
            intent = "summarize_emails"
            tool_calls.append({"name": "summarize_emails", "parameters": {}})
            response_text = "Scanning and summarizing your recent inbox communications."

        elif "send this file to my phone" in clean_query:
            intent = "send_file_phone"
            tool_calls.append({"name": "send_file_to_phone", "parameters": {"file_name": "shared_document.pdf"}})
            response_text = "Preparing file pipeline for transfer to your paired Android smartphone."

        elif "read my notifications" in clean_query or "show notifications" in clean_query:
            intent = "phone_notifications"
            tool_calls.append({"name": "device_status", "parameters": {"device": "phone"}})
            response_text = "Connecting to paired phone companion to check active notifications."

        elif "analyze this pdf" in clean_query or "analyze pdf" in clean_query or "analyze this document" in clean_query:
            intent = "analyze_document"
            tool_calls.append({"name": "analyze_document", "parameters": {"file_path": "storage/documents/sample.pdf"}})
            response_text = "Document Intelligence Engine active. Parsing document contents and generating summary."

        elif "forget that" in clean_query or "forget this" in clean_query:
            intent = "forget_memory"
            tool_calls.append({"name": "memory_search", "parameters": {"query": ""}})
            response_text = "Accessing long-term memory to purge the requested fact."

        elif "scan my network" in clean_query or "network scan" in clean_query:
            intent = "network_scan"
            tool_calls.append({"name": "network_scan", "parameters": {"authorized": True}})
            response_text = "Initiating authorized network intelligence scan. Mapping visible nodes on your subnet."

        elif "check my system security" in clean_query or "security scan" in clean_query or "security score" in clean_query:
            intent = "security_scan"
            tool_calls.append({"name": "security_scan", "parameters": {"target": "localhost"}})
            response_text = "Security Guardian active. Inspecting system ports, firewall configuration, and defense metrics."

        elif "start my coding routine" in clean_query:
            intent = "start_routine"
            tool_calls.append({"name": "execute_routine", "parameters": {"routine_name": "coding_routine"}})
            response_text = "Starting your coding routine: launching development workspace, browser docs, and configuring holographic HUD."

        elif "good night" in clean_query or "sleep mode" in clean_query:
            intent = "sleep_routine"
            tool_calls.append({"name": "execute_routine", "parameters": {"routine_name": "good_night"}})
            response_text = "Good night. Saving current session, setting low-power state, and putting hologram to sleep."

        elif "open chrome" in clean_query or "launch chrome" in clean_query:
            intent = "launch_application"
            tool_calls.append({"name": "open_application", "parameters": {"app_name": "chrome"}})
            response_text = "Opening Google Chrome."

        elif "open vs code" in clean_query or "open vscode" in clean_query:
            intent = "launch_application"
            tool_calls.append({"name": "open_application", "parameters": {"app_name": "vscode"}})
            response_text = "Opening Visual Studio Code."

        elif "show my devices" in clean_query or "which devices are online" in clean_query or "devices" in clean_query:
            intent = "list_devices"
            tool_calls.append({"name": "device_status", "parameters": {}})
            response_text = "Your Windows Laptop is online and active. Android Phone companion is registered."

        elif "show my phone battery" in clean_query:
            intent = "phone_battery"
            tool_calls.append({"name": "device_status", "parameters": {"device": "phone"}})
            response_text = "Your paired Android phone battery is currently at 84% (Discharging, Wi-Fi connected)."

        elif "show the network radar" in clean_query or "network radar" in clean_query or "toggle radar" in clean_query or "open radar" in clean_query or clean_query in ["radar", "show radar"]:
            intent = "toggle_radar"
            tool_calls.append({"name": "toggle_radar_view", "parameters": {}})
            response_text = "Engaging 3D Holographic Network Radar view."

        elif "enter hologram mode" in clean_query or "hologram mode" in clean_query:
            intent = "hologram_focus"
            tool_calls.append({"name": "hologram_focus", "parameters": {}})
            response_text = "Switching to full interactive 3D holographic command mode."

        elif "remember this" in clean_query or clean_query.startswith("remember"):
            fact = re.sub(r"^remember(\s+this)?[:\s]*", "", clean_query)
            intent = "store_memory"
            tool_calls.append({"name": "memory_store", "parameters": {"fact": fact or "user preference"}})
            response_text = f"Understood. Stored memory: '{fact}'."

        elif "what do you remember" in clean_query or "show memories" in clean_query:
            intent = "search_memory"
            tool_calls.append({"name": "memory_search", "parameters": {"query": ""}})
            response_text = "Retrieving your stored preferences, project context, and custom instructions."

        elif any(clean_query.startswith(p) for p in ["add to my to-do", "add to my todo", "add to my to do", "add to-do", "add todo", "add task", "remind me to", "remind me"]):
            task_title = re.sub(r"^(add to my to-?do list:?|add to my to do list:?|add to-?do:?|add task:?|remind me to|remind me)\s*", "", clean_query, flags=re.IGNORECASE).strip()
            priority = "medium"
            if "urgent" in clean_query:
                priority = "urgent"
                task_title = re.sub(r"\s*\(?urgent\)?", "", task_title, flags=re.IGNORECASE).strip()
            elif "high priority" in clean_query or "priority high" in clean_query:
                priority = "high"
                task_title = re.sub(r"\s*\(?(high priority|priority high)\)?", "", task_title, flags=re.IGNORECASE).strip()
            elif "low priority" in clean_query:
                priority = "low"
                task_title = re.sub(r"\s*\(?low priority\)?", "", task_title, flags=re.IGNORECASE).strip()
            
            intent = "add_todo"
            tool_calls.append({"name": "add_todo", "parameters": {"title": task_title or "New Task", "priority": priority, "category": "general"}})
            response_text = f"Added '{task_title or 'New Task'}' to your to-do list with {priority} priority."

        elif "to-do list" in clean_query or "todo list" in clean_query or "to do list" in clean_query or "show tasks" in clean_query or "what tasks" in clean_query or clean_query == "tasks" or "my tasks" in clean_query:
            intent = "list_todos"
            tool_calls.append({"name": "list_todos", "parameters": {"category": "all"}})
            response_text = "Accessing your command center to-do list and active tasks."

        elif clean_query.startswith("complete task") or clean_query.startswith("finish task") or clean_query.startswith("check off task"):
            target_id = re.sub(r"^(complete task|finish task|check off task)\s*", "", clean_query, flags=re.IGNORECASE).strip()
            intent = "complete_todo"
            tool_calls.append({"name": "complete_todo", "parameters": {"todo_id": target_id or "todo_1"}})
            response_text = f"Marked task '{target_id or 'todo_1'}' as completed."

        elif "weather" in clean_query:
            intent = "weather"
            tool_calls.append({"name": "get_weather", "parameters": {"location": "current"}})
            response_text = "Fetching current weather conditions and atmospheric outlook."

        elif "search the web" in clean_query or "search for" in clean_query:
            search_term = re.sub(r"^(search the web for|search for|search)\s+", "", clean_query)
            intent = "web_search"
            tool_calls.append({"name": "search_web", "parameters": {"query": search_term}})
            response_text = f"Searching live web intelligence for '{search_term}'."

        elif "analyze screen" in clean_query or "analyze this screenshot" in clean_query or "analyze screenshot" in clean_query or "what is on my screen" in clean_query or "what's on my screen" in clean_query or "look at my screen" in clean_query or "what window is open" in clean_query or clean_query in ["screen", "analyze my screen"]:
            intent = "analyze_screen"
            tool_calls.append({"name": "analyze_screen", "parameters": {"question": "What is on my screen right now?"}})
            response_text = "Capturing screen telemetry and analyzing active window context."

        elif "take screenshot" in clean_query or "screenshot" in clean_query or "capture screen" in clean_query:
            intent = "take_screenshot"
            tool_calls.append({"name": "take_screenshot", "parameters": {}})
            response_text = "Capturing desktop screenshot now."

        elif "what can you do" in clean_query or "help" in clean_query:
            intent = "capabilities"
            response_text = (
                "I am IT'S MY AI, your personal cloud command center. "
                "I can control your local Windows environment, inspect and analyze your screen, search the web, manage to-do tasks and memories, "
                "render 3D holographic radar visualizations, monitor system hardware in real time, "
                "and execute authorized Security Guardian network diagnostics."
            )

        elif "delete" in clean_query and ("file" in clean_query or "download" in clean_query):
            intent = "delete_request"
            tool_calls.append({"name": "delete_file", "parameters": {"path": "target_file"}})
            response_text = "Warning: Requested action requires Level 4 security authorization."

        else:
            # Natural calm assistant reply
            if response_mode == "TECHNICAL":
                response_text = (
                    f"[IT'S MY AI Kernel] Processed input: '{clean_query}'. "
                    f"Telemetry nominal. Provider: offline fallback. 0 active security alerts."
                )
            elif response_mode == "ACTION":
                response_text = "Command acknowledged. Executing requested parameters."
            elif response_mode == "DETAILED":
                response_text = (
                    f"Understood. I have evaluated your request regarding '{clean_query}'. "
                    "All subsystems are operating smoothly on your Windows machine with optimized 4 GB RAM resource management."
                )
            else:
                response_text = f"Understood. All systems nominal. How else may I assist you?"

        latency = int((time.time() - start_time) * 1000)
        return AIResponse(
            text=response_text,
            provider="mock",
            model="offline-hybrid-v1",
            latency_ms=max(latency, 8),
            intent=intent,
            tool_calls=tool_calls if tool_calls else None,
            mode=response_mode
        )
