"""
IT'S MY AI — Unified Tool Registry & Dispatcher
Implements Section 31:
- Comprehensive definitions of all available system tools
- Permission tier checking (Levels 1-4)
- User confirmation validation
- Execution routing, timeouts, error recovery, and structured audit logs
"""

import time
import inspect
from typing import Dict, Any, List, Optional
from backend.app.core.security import SecurityEngine, PermissionLevel
from backend.app.core.audit import AuditLogger
from backend.app.tools.windows_tools import WindowsTools
from backend.app.tools.web_tools import WebTools
from backend.app.tools.productivity_tools import ProductivityTools
from backend.app.services.memory_service import memory_service
from backend.app.services.device_service import device_service
from backend.app.services.automation_service import automation_service
from backend.app.services.security_guardian import security_guardian
from backend.app.services.todo_service import todo_service
from backend.app.services.vision_service import vision_service
from backend.app.services.document_service import document_service
from backend.app.services.media_service import media_service
from backend.app.services.browser_service import browser_service

class ToolDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        permission_level: PermissionLevel,
        target_device: str,
        handler: Any,
        requires_confirmation: bool = False,
        timeout_seconds: float = 10.0
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.permission_level = permission_level
        self.target_device = target_device
        self.handler = handler
        self.requires_confirmation = requires_confirmation
        self.timeout_seconds = timeout_seconds

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_all_tools()

    def register_tool(self, tool: ToolDefinition):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
                "permission_level": int(t.permission_level),
                "requires_confirmation": t.requires_confirmation,
                "target_device": t.target_device
            }
            for t in self._tools.values()
        ]

    async def execute_tool(
        self,
        name: str,
        parameters: Dict[str, Any],
        is_confirmed: bool = False,
        user_or_device: str = "local_user"
    ) -> Dict[str, Any]:
        """Executes a tool after security evaluation, permission enforcement, and logging."""
        tool = self.get_tool(name)
        if not tool:
            AuditLogger.log_event(
                event_type="tool_execution",
                action=f"Unknown tool '{name}'",
                status="not_found",
                user_or_device=user_or_device
            )
            return {"success": False, "error": f"Tool '{name}' is not registered."}

        # 1. Evaluate permission and confirmation requirements
        check = SecurityEngine.evaluate_action(name, parameters, is_confirmed=is_confirmed)
        if not check.allowed:
            AuditLogger.log_event(
                event_type="denied_action" if not check.requires_confirmation else "confirmation",
                action=f"Tool '{name}' blocked or awaiting confirmation",
                status="awaiting_confirmation" if check.requires_confirmation else "denied",
                user_or_device=user_or_device,
                permission_level=check.permission_level,
                details={"reason": check.reason}
            )
            return {
                "success": False,
                "requires_confirmation": check.requires_confirmation,
                "permission_level": check.permission_level,
                "warning_message": check.warning_message,
                "reason": check.reason,
                "tool_name": name,
                "parameters": parameters
            }

        # 2. Execute tool handler
        start_time = time.time()
        try:
            if inspect.iscoroutinefunction(tool.handler):
                result = await tool.handler(**parameters)
            else:
                result = tool.handler(**parameters)

            duration_ms = int((time.time() - start_time) * 1000)

            # 3. Audit log success
            AuditLogger.log_event(
                event_type="tool_execution",
                action=f"Executed '{name}'",
                status="success",
                user_or_device=user_or_device,
                permission_level=int(tool.permission_level),
                details={"duration_ms": duration_ms}
            )

            return {
                "success": True,
                "tool_name": name,
                "result": result,
                "duration_ms": duration_ms
            }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            AuditLogger.log_event(
                event_type="tool_execution",
                action=f"Failed to execute '{name}'",
                status="error",
                user_or_device=user_or_device,
                permission_level=int(tool.permission_level),
                details={"error": str(e), "duration_ms": duration_ms}
            )
            return {
                "success": False,
                "tool_name": name,
                "error": str(e),
                "duration_ms": duration_ms
            }

    def _register_all_tools(self):
        # LEVEL 1 — SAFE (Auto-execute)
        self.register_tool(ToolDefinition(
            name="open_application",
            description="Launches an approved desktop application (Chrome, VS Code, Notepad, Calc, Explorer).",
            parameters={"app_name": {"type": "string", "required": True}},
            permission_level=PermissionLevel.SAFE,
            target_device="laptop",
            handler=WindowsTools.open_application
        ))

        self.register_tool(ToolDefinition(
            name="open_website",
            description="Opens a webpage URL in the user's default browser.",
            parameters={"url": {"type": "string", "required": True}},
            permission_level=PermissionLevel.SAFE,
            target_device="laptop",
            handler=WebTools.open_website
        ))

        self.register_tool(ToolDefinition(
            name="search_web",
            description="Performs live search query on the web.",
            parameters={"query": {"type": "string", "required": True}},
            permission_level=PermissionLevel.SAFE,
            target_device="cloud",
            handler=WebTools.search_web
        ))

        self.register_tool(ToolDefinition(
            name="read_page_content",
            description="Navigates to a webpage and extracts its text with anti-injection protections.",
            parameters={"url": {"type": "string", "required": True}},
            permission_level=PermissionLevel.SAFE,
            target_device="cloud",
            handler=browser_service.fetch_page_content
        ))

        self.register_tool(ToolDefinition(
            name="summarize_webpage",
            description="Fetches a webpage and provides a concise AI summary of its content.",
            parameters={"url": {"type": "string", "required": True}, "question": {"type": "string", "default": None}},
            permission_level=PermissionLevel.SAFE,
            target_device="cloud",
            handler=browser_service.scrape_and_summarize
        ))

        self.register_tool(ToolDefinition(
            name="get_weather",
            description="Retrieves live temperature and atmospheric forecast.",
            parameters={"location": {"type": "string", "default": "current"}},
            permission_level=PermissionLevel.SAFE,
            target_device="cloud",
            handler=WebTools.get_weather
        ))

        self.register_tool(ToolDefinition(
            name="get_system_status",
            description="Reads real-time CPU, RAM, storage, and battery telemetry.",
            parameters={},
            permission_level=PermissionLevel.SAFE,
            target_device="laptop",
            handler=WindowsTools.get_system_status
        ))

        self.register_tool(ToolDefinition(
            name="device_status",
            description="Checks online/offline status and battery of paired devices.",
            parameters={"device": {"type": "string", "default": "all"}},
            permission_level=PermissionLevel.SAFE,
            target_device="cloud",
            handler=lambda device="all": device_service.list_devices() if device == "all" else device_service.get_device(device)
        ))

        self.register_tool(ToolDefinition(
            name="network_scan",
            description="Performs authorized local network discovery to map visible devices on user subnet.",
            parameters={"authorized": {"type": "boolean", "default": True}},
            permission_level=PermissionLevel.SAFE,
            target_device="laptop",
            handler=security_guardian.scan_authorized_network
        ))

        self.register_tool(ToolDefinition(
            name="security_scan",
            description="Performs Security Guardian defensive checks, open-port analysis, and score calculation.",
            parameters={"target": {"type": "string", "default": "localhost"}},
            permission_level=PermissionLevel.SAFE,
            target_device="laptop",
            handler=security_guardian.run_system_security_check
        ))

        self.register_tool(ToolDefinition(
            name="memory_search",
            description="Searches stored facts and preferences from long-term memory.",
            parameters={"query": {"type": "string", "default": ""}},
            permission_level=PermissionLevel.SAFE,
            target_device="cloud",
            handler=memory_service.search_memories
        ))

        self.register_tool(ToolDefinition(
            name="memory_store",
            description="Stores a new fact or user preference into long-term memory.",
            parameters={"fact": {"type": "string", "required": True}},
            permission_level=PermissionLevel.SAFE,
            target_device="cloud",
            handler=lambda fact: memory_service.store_memory(content=fact)
        ))

        self.register_tool(ToolDefinition(
            name="execute_routine",
            description="Runs a predefined automation routine (e.g., coding_routine, good_night).",
            parameters={"routine_name": {"type": "string", "required": True}},
            permission_level=PermissionLevel.SAFE,
            target_device="laptop",
            handler=automation_service.execute_routine
        ))

        self.register_tool(ToolDefinition(
            name="toggle_radar_view",
            description="Toggles the 3D Holographic Network Radar on the HUD.",
            parameters={},
            permission_level=PermissionLevel.SAFE,
            target_device="hologram",
            handler=lambda: {"mode": "RADAR", "active": True}
        ))

        self.register_tool(ToolDefinition(
            name="hologram_focus",
            description="Switches HUD to centered 3D holographic command mode.",
            parameters={},
            permission_level=PermissionLevel.SAFE,
            target_device="hologram",
            handler=lambda: {"mode": "HOLOGRAM", "active": True}
        ))

        self.register_tool(ToolDefinition(
            name="list_todos",
            description="Lists user to-do tasks with optional status and category filters.",
            parameters={"category": {"type": "string", "default": "all"}, "completed": {"type": "boolean", "default": None}},
            permission_level=PermissionLevel.SAFE,
            target_device="cloud",
            handler=lambda category="all", completed=None: todo_service.list_todos(category=category, completed=completed)
        ))

        self.register_tool(ToolDefinition(
            name="add_todo",
            description="Adds a new task to the user's to-do list.",
            parameters={"title": {"type": "string", "required": True}, "priority": {"type": "string", "default": "medium"}, "category": {"type": "string", "default": "general"}},
            permission_level=PermissionLevel.SAFE,
            target_device="cloud",
            handler=lambda title, priority="medium", category="general": todo_service.add_todo(title=title, priority=priority, category=category)
        ))

        self.register_tool(ToolDefinition(
            name="complete_todo",
            description="Marks a task as completed on the to-do list.",
            parameters={"todo_id": {"type": "string", "required": True}},
            permission_level=PermissionLevel.SAFE,
            target_device="cloud",
            handler=lambda todo_id: todo_service.toggle_todo(todo_id=todo_id, completed=True)
        ))

        self.register_tool(ToolDefinition(
            name="set_system_volume",
            description="Sets or adjusts the Windows computer speaker volume (0 to 100).",
            parameters={"level": {"type": "integer", "required": True}},
            permission_level=PermissionLevel.SAFE,
            target_device="laptop",
            handler=WindowsTools.set_system_volume
        ))

        self.register_tool(ToolDefinition(
            name="media_control",
            description="Controls media playback (play, pause, next, previous, mute).",
            parameters={"action": {"type": "string", "required": True}},
            permission_level=PermissionLevel.SAFE,
            target_device="laptop",
            handler=media_service.control_playback
        ))

        self.register_tool(ToolDefinition(
            name="play_youtube",
            description="Searches and plays music, videos, or playlists on YouTube.",
            parameters={"query": {"type": "string", "required": True}},
            permission_level=PermissionLevel.SAFE,
            target_device="laptop",
            handler=media_service.play_youtube
        ))

        self.register_tool(ToolDefinition(
            name="manage_clipboard",
            description="Reads from or copies text into the Windows system clipboard.",
            parameters={"action": {"type": "string", "default": "get"}, "text": {"type": "string", "default": ""}},
            permission_level=PermissionLevel.SAFE,
            target_device="laptop",
            handler=WindowsTools.manage_clipboard
        ))

        # LEVEL 2 — PERSONAL
        self.register_tool(ToolDefinition(
            name="create_folder",
            description="Creates a new directory folder on the local storage.",
            parameters={"path": {"type": "string", "required": True}},
            permission_level=PermissionLevel.PERSONAL,
            target_device="laptop",
            handler=lambda path: WindowsTools.manage_files("create_folder", path)
        ))

        self.register_tool(ToolDefinition(
            name="copy_file",
            description="Copies a file from source to destination directory.",
            parameters={"src": {"type": "string", "required": True}, "dst": {"type": "string", "required": True}},
            permission_level=PermissionLevel.PERSONAL,
            target_device="laptop",
            handler=lambda src, dst: WindowsTools.manage_files("copy", src, dst)
        ))

        self.register_tool(ToolDefinition(
            name="move_file",
            description="Moves or renames a file on the local computer.",
            parameters={"src": {"type": "string", "required": True}, "dst": {"type": "string", "required": True}},
            permission_level=PermissionLevel.PERSONAL,
            target_device="laptop",
            handler=lambda src, dst: WindowsTools.manage_files("move", src, dst)
        ))

        self.register_tool(ToolDefinition(
            name="delete_todo",
            description="Removes a specific task from the to-do list.",
            parameters={"todo_id": {"type": "string", "required": True}},
            permission_level=PermissionLevel.PERSONAL,
            target_device="cloud",
            handler=lambda todo_id: todo_service.delete_todo(todo_id=todo_id)
        ))

        self.register_tool(ToolDefinition(
            name="take_screenshot",
            description="Captures desktop screenshot for visual analysis.",
            parameters={},
            permission_level=PermissionLevel.PERSONAL,
            target_device="laptop",
            handler=WindowsTools.take_screenshot
        ))

        self.register_tool(ToolDefinition(
            name="analyze_screen",
            description="Captures the desktop screen and uses AI vision to analyze the active window and visual content.",
            parameters={"question": {"type": "string", "default": "What is on my screen right now?"}},
            permission_level=PermissionLevel.PERSONAL,
            target_device="laptop",
            handler=vision_service.analyze_screen
        ))

        self.register_tool(ToolDefinition(
            name="find_file",
            description="Searches local filesystem for a file matching query.",
            parameters={"query": {"type": "string", "required": True}},
            permission_level=PermissionLevel.PERSONAL,
            target_device="laptop",
            handler=WindowsTools.find_file
        ))

        self.register_tool(ToolDefinition(
            name="analyze_document",
            description="Extracts and analyzes contents of a local PDF, DOCX, CSV, or text file with AI summarization.",
            parameters={"file_path": {"type": "string", "required": True}, "question": {"type": "string", "default": None}},
            permission_level=PermissionLevel.PERSONAL,
            target_device="laptop",
            handler=document_service.analyze_document
        ))

        self.register_tool(ToolDefinition(
            name="summarize_pdf",
            description="Parses a PDF document and extracts key summaries and action items.",
            parameters={"file_path": {"type": "string", "required": True}},
            permission_level=PermissionLevel.PERSONAL,
            target_device="laptop",
            handler=lambda file_path: document_service.analyze_document(file_path=file_path, question="Summarize this PDF document.")
        ))

        self.register_tool(ToolDefinition(
            name="summarize_emails",
            description="Fetches and summarizes recent inbox messages.",
            parameters={},
            permission_level=PermissionLevel.PERSONAL,
            target_device="cloud",
            handler=ProductivityTools.summarize_emails
        ))

        self.register_tool(ToolDefinition(
            name="get_calendar_events",
            description="Reads scheduled events from calendar.",
            parameters={},
            permission_level=PermissionLevel.PERSONAL,
            target_device="cloud",
            handler=ProductivityTools.get_calendar_events
        ))

        # LEVEL 3 — SENSITIVE (Requires confirmation)
        self.register_tool(ToolDefinition(
            name="send_email",
            description="Dispatches an email message to a specified recipient.",
            parameters={"recipient": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
            permission_level=PermissionLevel.SENSITIVE,
            requires_confirmation=True,
            target_device="cloud",
            handler=ProductivityTools.send_email
        ))

        self.register_tool(ToolDefinition(
            name="create_calendar_event",
            description="Adds a scheduled event to the calendar.",
            parameters={"title": {"type": "string"}, "time_str": {"type": "string"}},
            permission_level=PermissionLevel.SENSITIVE,
            requires_confirmation=True,
            target_device="cloud",
            handler=ProductivityTools.create_calendar_event
        ))

        self.register_tool(ToolDefinition(
            name="phone_notification",
            description="Pushes a high-priority alert to the user's paired mobile phone.",
            parameters={"message": {"type": "string"}},
            permission_level=PermissionLevel.SENSITIVE,
            requires_confirmation=False,
            target_device="phone",
            handler=ProductivityTools.send_phone_notification
        ))

        self.register_tool(ToolDefinition(
            name="send_file_to_phone",
            description="Transfers a local file to the user's paired Android device.",
            parameters={"file_name": {"type": "string"}},
            permission_level=PermissionLevel.SENSITIVE,
            requires_confirmation=True,
            target_device="phone",
            handler=lambda file_name: device_service.send_file_to_device("mobile", file_name)
        ))

        # LEVEL 4 — DANGEROUS (Explicit confirmation & safeguards)
        self.register_tool(ToolDefinition(
            name="close_application",
            description="Forces closure of an active desktop process.",
            parameters={"process_name": {"type": "string"}},
            permission_level=PermissionLevel.DANGEROUS,
            requires_confirmation=True,
            target_device="laptop",
            handler=WindowsTools.close_application
        ))

        self.register_tool(ToolDefinition(
            name="lock_computer",
            description="Instantly locks the Windows computer workstation.",
            parameters={},
            permission_level=PermissionLevel.DANGEROUS,
            requires_confirmation=True,
            target_device="laptop",
            handler=WindowsTools.lock_workstation
        ))

        self.register_tool(ToolDefinition(
            name="wipe_memory",
            description="Permanently erases all long-term memory stored for the user.",
            parameters={},
            permission_level=PermissionLevel.DANGEROUS,
            requires_confirmation=True,
            target_device="cloud",
            handler=memory_service.clear_all_memories
        ))

        self.register_tool(ToolDefinition(
            name="delete_file",
            description="Permanently deletes a file or directory from local storage.",
            parameters={"path": {"type": "string", "required": True}},
            permission_level=PermissionLevel.DANGEROUS,
            requires_confirmation=True,
            target_device="laptop",
            handler=lambda path: WindowsTools.manage_files("delete", path)
        ))

        self.register_tool(ToolDefinition(
            name="restart_computer",
            description="Initiates an authorized restart of the Windows operating system.",
            parameters={},
            permission_level=PermissionLevel.DANGEROUS,
            requires_confirmation=True,
            target_device="laptop",
            handler=WindowsTools.restart_computer
        ))

        self.register_tool(ToolDefinition(
            name="shutdown_computer",
            description="Initiates an authorized shutdown of the Windows operating system.",
            parameters={},
            permission_level=PermissionLevel.DANGEROUS,
            requires_confirmation=True,
            target_device="laptop",
            handler=WindowsTools.shutdown_computer
        ))

tool_registry = ToolRegistry()
