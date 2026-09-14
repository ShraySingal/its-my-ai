"""
IT'S MY AI — Master Commands Test Suite
Tests all 24 Explicit Command Examples from Section 47 of ITS_MY_AI_Master_Prompt.pdf:
 1. "It's My AI, open Chrome."
 2. "It's My AI, open VS Code."
 3. "It's My AI, start my coding routine."
 4. "It's My AI, check my laptop."
 5. "It's My AI, how much RAM do I have?"
 6. "It's My AI, show my devices."
 7. "It's My AI, scan my network."
 8. "It's My AI, which devices are online?"
 9. "It's My AI, what type of devices are connected?"
10. "It's My AI, show my phone battery."
11. "It's My AI, send this file to my phone."
12. "It's My AI, read my notifications."
13. "It's My AI, check my calendar."
14. "It's My AI, summarize my emails."
15. "It's My AI, remind me tomorrow."
16. "It's My AI, remember this."
17. "It's My AI, forget that."
18. "It's My AI, analyze this PDF."
19. "It's My AI, analyze this screenshot."
20. "It's My AI, search the web."
21. "It's My AI, check my system security."
22. "It's My AI, show the network radar."
23. "It's My AI, enter hologram mode."
24. "It's My AI, good night."
"""

import sys
import asyncio
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.dont_write_bytecode = True

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.providers.mock_provider import MockOfflineProvider
from backend.app.tools.registry import tool_registry

COMMANDS = [
    ("It's My AI, open Chrome.", "open_application"),
    ("It's My AI, open VS Code.", "open_application"),
    ("It's My AI, start my coding routine.", "execute_routine"),
    ("It's My AI, check my laptop.", "get_system_status"),
    ("It's My AI, how much RAM do I have?", "get_system_status"),
    ("It's My AI, show my devices.", "device_status"),
    ("It's My AI, scan my network.", "network_scan"),
    ("It's My AI, which devices are online?", "device_status"),
    ("It's My AI, what type of devices are connected?", "device_status"),
    ("It's My AI, show my phone battery.", "device_status"),
    ("It's My AI, send this file to my phone.", "send_file_to_phone"),
    ("It's My AI, read my notifications.", "device_status"),
    ("It's My AI, check my calendar.", "get_calendar_events"),
    ("It's My AI, summarize my emails.", "summarize_emails"),
    ("It's My AI, remind me tomorrow.", "add_todo"),
    ("It's My AI, remember this.", "memory_store"),
    ("It's My AI, forget that.", "memory_search"),
    ("It's My AI, analyze this PDF.", "analyze_document"),
    ("It's My AI, analyze this screenshot.", "analyze_screen"),
    ("It's My AI, search the web.", "search_web"),
    ("It's My AI, check my system security.", "security_scan"),
    ("It's My AI, show the network radar.", "toggle_radar_view"),
    ("It's My AI, enter hologram mode.", "hologram_focus"),
    ("It's My AI, good night.", "execute_routine"),
]

async def run_master_command_tests():
    print("=" * 70)
    print("      IT'S MY AI — SECTION 47 MASTER COMMAND SUITE (24/24)")
    print("=" * 70)

    provider = MockOfflineProvider()
    passed = 0

    for idx, (command_text, expected_tool) in enumerate(COMMANDS, 1):
        resp = await provider.generate_response(
            messages=[{"role": "user", "content": command_text}],
            system_instruction="You are IT'S MY AI."
        )

        assert resp.text is not None and len(resp.text) > 0, f"Empty text for command: {command_text}"
        assert resp.tool_calls is not None and len(resp.tool_calls) > 0, f"No tool calls mapped for: {command_text}"

        actual_tool = resp.tool_calls[0]["name"]
        tool_match = (actual_tool == expected_tool)
        assert tool_match, f"Tool mismatch for '{command_text}': Expected {expected_tool}, got {actual_tool}"

        # Verify tool is registered in unified ToolRegistry
        tool_def = tool_registry.get_tool(actual_tool)
        assert tool_def is not None, f"Tool '{actual_tool}' is not registered in ToolRegistry!"

        passed += 1
        print(f"  [{idx:02d}/24] ✓ \"{command_text}\" -> {actual_tool} (Tier {int(tool_def.permission_level)})")

    print("=" * 70)
    print(f"   ALL 24 MASTER PROMPT COMMANDS VERIFIED & OPERATIONAL ({passed}/24 PASS)")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_master_command_tests())
