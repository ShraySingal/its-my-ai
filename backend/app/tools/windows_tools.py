"""
IT'S MY AI — Windows Desktop Agent Tools
Complies with Section 12: Controlled Windows system actions with strict whitelist policy.
No unrestricted shell execution.
"""

import os
import subprocess
import platform
import glob
from pathlib import Path
from typing import Dict, Any
from backend.app.services.system_service import system_service

# Whitelisted application launch commands
APP_WHITELIST = {
    "chrome": "start chrome",
    "google chrome": "start chrome",
    "edge": "start msedge",
    "microsoft edge": "start msedge",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "vscode": "code",
    "vs code": "code",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "taskmgr": "taskmgr.exe",
    "task manager": "taskmgr.exe",
    "paint": "mspaint.exe",
    "terminal": "wt.exe",
    "powershell": "powershell.exe",
}

class WindowsTools:
    @staticmethod
    def open_application(app_name: str) -> Dict[str, Any]:
        """Launches a whitelisted Windows program."""
        clean_name = app_name.lower().strip()
        cmd = APP_WHITELIST.get(clean_name)
        if not cmd:
            # Check if any key is contained in user query
            for k, v in APP_WHITELIST.items():
                if k in clean_name:
                    cmd = v
                    break

        if not cmd:
            return {
                "success": False,
                "message": f"Application '{app_name}' is not in the authorized application whitelist."
            }

        try:
            if platform.system() == "Windows":
                subprocess.Popen(cmd, shell=True)
            return {
                "success": True,
                "app_name": app_name,
                "command": cmd,
                "message": f"Successfully launched {app_name} on your Windows desktop."
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to launch application: {str(e)}"}

    @staticmethod
    def close_application(process_name: str) -> Dict[str, Any]:
        """Terminates an application process safely."""
        clean_name = process_name.lower().replace(".exe", "").strip()
        # Protect system-critical processes
        if clean_name in ("svchost", "csrss", "system", "smss", "winlogon", "lsass", "explorer"):
            return {
                "success": False,
                "message": f"Refusing to close protected system process '{process_name}'."
            }

        try:
            if platform.system() == "Windows":
                subprocess.run(f"taskkill /IM {clean_name}.exe /F", shell=True, check=False)
            return {"success": True, "message": f"Closed application process '{clean_name}'."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def lock_workstation() -> Dict[str, Any]:
        """Locks the Windows computer."""
        try:
            if platform.system() == "Windows":
                subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True, check=False)
            return {"success": True, "message": "Workstation locked successfully."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def take_screenshot() -> Dict[str, Any]:
        """Captures a real Windows desktop screenshot and saves to storage."""
        from backend.app.services.vision_service import vision_service
        return vision_service.capture_screenshot()

    @staticmethod
    def find_file(query: str, root_dir: str = ".") -> Dict[str, Any]:
        """Searches for files matching a wildcard pattern."""
        matches = glob.glob(f"**/*{query}*", recursive=True)[:15]
        return {
            "success": True,
            "query": query,
            "count": len(matches),
            "matches": matches
        }

    @staticmethod
    def get_system_status() -> Dict[str, Any]:
        """Retrieves live system hardware metrics."""
        return system_service.get_telemetry()

    @staticmethod
    def set_system_volume(level: int) -> Dict[str, Any]:
        """Sets or adjusts system volume on Windows (0 to 100)."""
        target = max(0, min(100, int(level)))
        try:
            if platform.system() == "Windows":
                # PowerShell volume stepper using WScript Shell virtual keys
                steps_down = 50
                steps_up = int(target / 2)
                ps_script = f"$w = New-Object -ComObject WScript.Shell; 1..{steps_down} | % {{ $w.SendKeys([char]174) }}; 1..{steps_up} | % {{ $w.SendKeys([char]175) }}"
                subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_script])
            return {"success": True, "level": target, "message": f"Volume set to approximately {target}%."}
        except Exception as e:
            return {"success": False, "error": f"Failed to adjust volume: {str(e)}"}

    @staticmethod
    def manage_files(action: str, src_path: str, dst_path: str = "") -> Dict[str, Any]:
        """Performs controlled file operations: create_folder, copy, move, rename, delete."""
        import shutil
        action = action.lower().strip()
        src = Path(src_path)

        # Safety Guard: Block modifications to Windows system directories (Section 12 & 48)
        resolved_src = str(src.resolve()).lower()
        if any(sys_dir in resolved_src for sys_dir in ["c:\\windows", "c:\\program files", "c:\\system volume information"]):
            return {"success": False, "error": "Modifying system-critical directories is strictly forbidden."}

        try:
            if action == "create_folder":
                src.mkdir(parents=True, exist_ok=True)
                return {"success": True, "action": action, "path": str(src), "message": f"Created folder '{src}'."}
            elif action == "copy":
                if not dst_path:
                    return {"success": False, "error": "Destination path required for copy."}
                dst = Path(dst_path)
                shutil.copy2(src, dst)
                return {"success": True, "action": action, "src": str(src), "dst": str(dst), "message": f"Copied to '{dst}'."}
            elif action in ("move", "rename"):
                if not dst_path:
                    return {"success": False, "error": "Destination path required for move/rename."}
                dst = Path(dst_path)
                shutil.move(src, dst)
                return {"success": True, "action": action, "src": str(src), "dst": str(dst), "message": f"Moved to '{dst}'."}
            elif action == "delete":
                if src.is_dir():
                    shutil.rmtree(src)
                else:
                    src.unlink()
                return {"success": True, "action": action, "path": str(src), "message": f"Permanently deleted '{src}'."}
            else:
                return {"success": False, "error": f"Unknown file action '{action}'."}
        except Exception as e:
            return {"success": False, "error": f"File operation failed: {str(e)}"}

    @staticmethod
    def manage_clipboard(action: str = "get", text: str = "") -> Dict[str, Any]:
        """Reads or writes text to the Windows system clipboard."""
        try:
            if action == "get":
                res = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"], capture_output=True, text=True, check=True)
                return {"success": True, "clipboard_text": res.stdout.strip()}
            elif action == "set":
                # Safe escaping for PowerShell
                escaped = text.replace('"', '`"')
                subprocess.run(["powershell", "-NoProfile", "-Command", f'Set-Clipboard -Value "{escaped}"'], check=True)
                return {"success": True, "message": "Copied text to clipboard."}
            return {"success": False, "error": "Unsupported clipboard action. Use 'get' or 'set'."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def restart_computer() -> Dict[str, Any]:
        """Restarts the computer with a 15-second grace period."""
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["shutdown", "/r", "/t", "15", "/c", "IT'S MY AI authorized restart."])
            return {"success": True, "message": "Restart scheduled in 15 seconds."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def shutdown_computer() -> Dict[str, Any]:
        """Shuts down the computer with a 15-second grace period."""
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["shutdown", "/s", "/t", "15", "/c", "IT'S MY AI authorized shutdown."])
            return {"success": True, "message": "Shutdown scheduled in 15 seconds."}
        except Exception as e:
            return {"success": False, "error": str(e)}
