"""
IT'S MY AI — Universal Application Launcher
Checks environment, starts FastAPI/Uvicorn server, and opens the Holographic Command Center.
Strictly optimized for 4 GB RAM Windows environment.
"""

import sys
import os
import time
import webbrowser
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.dont_write_bytecode = True

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                        IT'S MY AI                            ║
    ║               Personal Cloud AI Command Center               ║
    ║                Optimized for 4 GB RAM Windows                ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    missing = []
    for pkg in ["fastapi", "uvicorn", "pydantic"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    return missing

def main():
    print_banner()
    print("[1/3] Validating system environment...")
    print(f"      Host Platform: {sys.platform} | Python {sys.version.split()[0]}")
    print(f"      Workspace: {BASE_DIR}")

    missing = check_dependencies()
    if missing:
        print(f"[!] Missing required dependencies: {', '.join(missing)}")
        print("    Installing dependencies from requirements.txt...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(BASE_DIR / "requirements.txt")], check=False)

    # Ensure browser extension icons are generated
    icons_path = BASE_DIR / "extension" / "icons" / "icon128.png"
    if not icons_path.exists():
        try:
            from extension.generate_icons import main as gen_icons
            gen_icons()
        except Exception:
            pass


    import socket

    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    local_ip = get_local_ip()
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")

    local_url = f"http://127.0.0.1:{port}"
    mobile_url = f"http://{local_ip}:{port}"

    print(f"[2/3] Initializing IT'S MY AI FastAPI Server...")
    print(f"      ▶ Laptop Access:  {local_url}")
    print(f"      ▶ Mobile Phone:   {mobile_url}")
    print("      ----------------------------------------------------------")

    # Launch browser after slight delay
    def open_browser():
        time.sleep(1.2)
        print(f"[3/3] Launching Command Center on Laptop: {local_url}")
        webbrowser.open(local_url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    try:
        import uvicorn
        uvicorn.run(
            "backend.app.main:app",
            host=host,
            port=port,
            reload=False,
            log_level="info",
            access_log=False  # Reduce I/O overhead on low RAM
        )
    except Exception as e:
        print(f"[ERROR] Failed to start uvicorn: {e}")
        print("Starting lightweight fallback HTTP server...")
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        os.chdir(str(BASE_DIR / "frontend"))
        server = HTTPServer((host, port), SimpleHTTPRequestHandler)
        print(f"Lightweight static HUD server running at {app_url}")
        server.serve_forever()

if __name__ == "__main__":
    main()
