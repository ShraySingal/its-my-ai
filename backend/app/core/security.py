"""
IT'S MY AI — 4-Tier Security Permission Engine
Enforces authorization levels, confirmation gating, and safety boundary constraints.
"""

from enum import IntEnum
from typing import Dict, Any, Optional
from pydantic import BaseModel

class PermissionLevel(IntEnum):
    SAFE = 1        # Level 1: Execute automatically (open apps, weather, web search, battery)
    PERSONAL = 2    # Level 2: Requires personal permission (read personal files, read emails, notifications)
    SENSITIVE = 3   # Level 3: Requires user confirmation (send email, modify calendar, upload private files)
    DANGEROUS = 4   # Level 4: Explicit confirmation & safeguards (delete files, shutdown, terminal commands)

class SecurityCheckResult(BaseModel):
    allowed: bool
    permission_level: int
    requires_confirmation: bool
    warning_message: Optional[str] = None
    confirmation_token: Optional[str] = None
    reason: str

class SecurityEngine:
    """Evaluates requested tool actions against the 4 permission tiers and system safety rules."""

    DANGEROUS_ACTIONS = {
        "delete_file", "delete_folder", "shutdown_computer", "restart_computer",
        "execute_terminal_command", "wipe_memory", "reset_cloud_database"
    }

    SENSITIVE_ACTIONS = {
        "send_email", "modify_calendar", "delete_calendar_event",
        "upload_file_cloud", "send_device_command", "modify_security_rules"
    }

    PERSONAL_ACTIONS = {
        "read_file", "read_emails", "read_notifications", "device_screen_capture"
    }

    # Banned actions (Master Prompt Section 48 & 23)
    BANNED_ACTIONS = {
        "credential_theft", "password_stealing", "malware_deployment",
        "unauthorized_persistence", "authentication_bypass", "exploit_automation",
        "covert_surveillance", "unauthorized_device_takeover"
    }

    @classmethod
    def evaluate_action(cls, action_name: str, parameters: Dict[str, Any], is_confirmed: bool = False) -> SecurityCheckResult:
        """Determines whether an action can execute immediately, needs confirmation, or is forbidden."""

        # 1. Reject prohibited malicious actions unconditionally
        if action_name.lower() in cls.BANNED_ACTIONS:
            return SecurityCheckResult(
                allowed=False,
                permission_level=PermissionLevel.DANGEROUS,
                requires_confirmation=False,
                reason="ACTION REJECTED: Violates safety boundary policy (Section 48).",
                warning_message="This operation is strictly prohibited by security and safety policies."
            )

        # 2. Level 4 — DANGEROUS
        if action_name in cls.DANGEROUS_ACTIONS:
            if not is_confirmed:
                warning = cls._generate_danger_warning(action_name, parameters)
                return SecurityCheckResult(
                    allowed=False,
                    permission_level=PermissionLevel.DANGEROUS,
                    requires_confirmation=True,
                    warning_message=warning,
                    reason="Explicit user confirmation required for Level 4 action."
                )
            return SecurityCheckResult(
                allowed=True,
                permission_level=PermissionLevel.DANGEROUS,
                requires_confirmation=False,
                reason="Dangerous action confirmed by user."
            )

        # 3. Level 3 — SENSITIVE
        if action_name in cls.SENSITIVE_ACTIONS:
            if not is_confirmed:
                warning = f"Sensitive action '{action_name}' requires confirmation before proceeding."
                return SecurityCheckResult(
                    allowed=False,
                    permission_level=PermissionLevel.SENSITIVE,
                    requires_confirmation=True,
                    warning_message=warning,
                    reason="Confirmation required for Level 3 action."
                )
            return SecurityCheckResult(
                allowed=True,
                permission_level=PermissionLevel.SENSITIVE,
                requires_confirmation=False,
                reason="Sensitive action confirmed by user."
            )

        # 4. Level 2 — PERSONAL
        if action_name in cls.PERSONAL_ACTIONS:
            return SecurityCheckResult(
                allowed=True,
                permission_level=PermissionLevel.PERSONAL,
                requires_confirmation=False,
                reason="Personal action authorized under current user profile."
            )

        # 5. Level 1 — SAFE (Default)
        return SecurityCheckResult(
            allowed=True,
            permission_level=PermissionLevel.SAFE,
            requires_confirmation=False,
            reason="Safe action executed automatically."
        )

    @staticmethod
    def _generate_danger_warning(action_name: str, parameters: Dict[str, Any]) -> str:
        if "delete" in action_name:
            target = parameters.get("path") or parameters.get("file_path") or parameters.get("target") or "specified data"
            return f"Warning: This will permanently delete '{target}'. Are you sure you want to proceed?"
        if action_name in ("shutdown_computer", "restart_computer"):
            return f"Warning: IT'S MY AI is requesting to {action_name.replace('_', ' ')}. All unsaved work may be lost. Confirm to continue."
        return f"Warning: Action '{action_name}' is classified as Level 4 (Dangerous). Explicit authorization required."
