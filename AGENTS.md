# IT'S MY AI — Agent Rules & Knowledge Base

This project is **IT'S MY AI**, a personal cloud AI command center inspired by JARVIS/FRIDAY and architected strictly for low-resource hardware (**Intel Core i5-1235U with 4 GB RAM on Windows 64-bit**).

## Core Architecture Principles
1. **Cloud-First & API-First**: Heavy AI computation and models reside in the cloud (Gemini, Groq, OpenAI). The local computer primarily handles the UI, Three.js hologram, hardware telemetry, and local whitelisted tool dispatch.
2. **Zero-Friction Offline Degradation**: The system operates with full functionality out of the box using an offline fallback mock provider if cloud keys are absent or internet drops.
3. **4-Tier Security Permission System**:
   - `Level 1 (SAFE)`: Auto-executed (weather, time, web search, system telemetry).
   - `Level 2 (PERSONAL)`: Personal data (notifications, emails, files).
   - `Level 3 (SENSITIVE)`: State-mutating operations (sending emails, modifying calendars). Requires user confirmation.
   - `Level 4 (DANGEROUS)`: Disruptive actions (delete files, lock workstation, system commands). Requires explicit modal confirmation with impact warnings.
4. **Anti-Prompt-Injection**: All untrusted external inputs (web pages, documents, emails) must be wrapped in `<UNTRUSTED_EXTERNAL_DATA>` tags.
5. **Structured Audit Trail**: Every tool invocation, confirmation, denial, and security check is logged to `storage/audit.log`.

## Directory Map
- `backend/app/main.py`: FastAPI server mounting `/static`, `/css`, `/js`, and `/`.
- `backend/app/routers/`: Modular endpoints (`ai_router`, `system_router`, `tools_router`, `memory_router`, `devices_router`, `security_router`, `automation_router`, `ws_router`).
- `frontend/`: 3D Holographic Command Center (Three.js WebGL avatar, audio visualizer, radar, telemetry).
- `extension/`: Manifest V3 browser companion for Chrome, Edge, and Chromium-based browsers.
- `.vscode/`: Workspace recommendations (`extensions.json`), RAM-optimized settings (`settings.json`), and debug configurations (`launch.json`).
