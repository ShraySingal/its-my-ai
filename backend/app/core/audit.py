"""
IT'S MY AI — Structured Audit Logging Engine
Complies with Section 46: Records system security events, tool invocations, confirmations, and denials.
Never logs secrets, API keys, or raw passwords.
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.app.config import settings

class AuditLogger:
    """Manages append-only audit records and provides real-time event retrieval for the HUD."""

    _memory_cache: List[Dict[str, Any]] = []
    _max_cache_size: int = 200

    @classmethod
    def log_event(
        cls,
        event_type: str,
        action: str,
        status: str,
        user_or_device: str = "local_user",
        details: Optional[Dict[str, Any]] = None,
        permission_level: int = 1
    ) -> Dict[str, Any]:
        """
        Record an audit log entry.
        event_type: 'login', 'device_pairing', 'tool_execution', 'sensitive_action',
                    'confirmation', 'denied_action', 'api_failure', 'security_alert',
                    'memory_event', 'file_upload', 'remote_command'
        """
        safe_details = cls._sanitize_details(details or {})
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "epoch_ms": int(time.time() * 1000),
            "event_type": event_type,
            "action": action,
            "status": status,
            "user_or_device": user_or_device,
            "permission_level": permission_level,
            "details": safe_details
        }

        # Keep in memory cache for fast HUD retrieval
        cls._memory_cache.append(entry)
        if len(cls._memory_cache) > cls._max_cache_size:
            cls._memory_cache.pop(0)

        # Append to persistent audit log file
        try:
            with open(settings.AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass  # Fail-safe: auditing should never crash the main loop

        return entry

    @classmethod
    def get_recent_events(cls, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the most recent audit events."""
        return cls._memory_cache[-limit:][::-1]

    @classmethod
    def _sanitize_details(cls, details: Dict[str, Any]) -> Dict[str, Any]:
        """Strip sensitive credentials, passwords, or tokens."""
        sanitized = {}
        redacted_keys = {"password", "secret", "token", "key", "api_key", "auth", "credential"}
        for k, v in details.items():
            if any(rk in k.lower() for rk in redacted_keys):
                sanitized[k] = "[REDACTED]"
            elif isinstance(v, dict):
                sanitized[k] = cls._sanitize_details(v)
            else:
                sanitized[k] = v
        return sanitized
