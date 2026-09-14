"""
IT'S MY AI — Core Configuration
Manages environment variables, defaults, and security policies.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Try loading dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

class Settings:
    PROJECT_NAME: str = "IT'S MY AI"
    VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # AI Provider configuration
    DEFAULT_AI_PROVIDER: str = os.getenv("DEFAULT_AI_PROVIDER", "mock")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Supabase (Cloud Database, pgvector, Storage, Auth)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # External APIs
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")

    # Security settings
    REQUIRE_CONFIRMATION_FOR_SENSITIVE: bool = os.getenv("REQUIRE_CONFIRMATION_FOR_SENSITIVE", "true").lower() == "true"
    REQUIRE_CONFIRMATION_FOR_DANGEROUS: bool = os.getenv("REQUIRE_CONFIRMATION_FOR_DANGEROUS", "true").lower() == "true"

    # Device identity
    DEVICE_NAME: str = os.getenv("DEVICE_NAME", "Windows Command Center")
    DEVICE_TYPE: str = os.getenv("DEVICE_TYPE", "Laptop")

    # Local Storage Paths
    STORAGE_DIR: Path = STORAGE_DIR
    MEMORIES_FILE: Path = STORAGE_DIR / "memories.json"
    AUDIT_LOG_FILE: Path = STORAGE_DIR / "audit.log"
    DEVICES_FILE: Path = STORAGE_DIR / "devices.json"
    ROUTINES_FILE: Path = STORAGE_DIR / "routines.json"
    TODOS_FILE: Path = STORAGE_DIR / "todos.json"
    SCREENSHOT_FILE: Path = STORAGE_DIR / "latest_screenshot.png"

settings = Settings()
