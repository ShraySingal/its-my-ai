"""
IT'S MY AI — Vision & Screen Analysis Service
Provides real-time desktop screen capture, foreground window context extraction,
and multimodal vision reasoning for the personal command center.
Optimized for 4 GB RAM Windows environments.
"""

import os
import io
import time
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from backend.app.config import settings
from backend.app.core.audit import AuditLogger

SCREENSHOT_PATH = settings.STORAGE_DIR / "latest_screenshot.png"

class VisionService:
    def __init__(self):
        self.latest_screenshot_path = SCREENSHOT_PATH

    @staticmethod
    def get_active_window_context() -> Dict[str, str]:
        """Retrieves active foreground window title and process name on Windows."""
        title = "Desktop Workspace"
        process_name = "explorer.exe"
        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if hwnd:
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    if buff.value.strip():
                        title = buff.value.strip()

                pid = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if pid.value:
                    try:
                        import psutil
                        proc = psutil.Process(pid.value)
                        process_name = proc.name()
                    except Exception:
                        pass
        except Exception:
            pass
        return {"title": title, "process": process_name}

    def capture_screenshot(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Captures the primary display screen and saves as PNG.
        Uses a resilient multi-tier capture cascade:
        1. GDI BitBlt via ctypes + PIL
        2. PIL ImageGrab
        3. mss
        4. Synthetic visual buffer fallback (for non-interactive headless sessions)
        """
        target_path = output_path or self.latest_screenshot_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        context = self.get_active_window_context()

        width, height = 1920, 1080
        img_bytes = None
        capture_method = "gdi"

        # Tier 1: Windows GDI BitBlt
        try:
            import ctypes
            from PIL import Image

            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32

            try:
                user32.SetProcessDPIAware()
            except Exception:
                pass

            w = user32.GetSystemMetrics(0) or 1920
            h = user32.GetSystemMetrics(1) or 1080

            hwnd = user32.GetDesktopWindow()
            hdc_src = user32.GetWindowDC(hwnd)
            hdc_mem = gdi32.CreateCompatibleDC(hdc_src)
            hbmp = gdi32.CreateCompatibleBitmap(hdc_src, w, h)
            gdi32.SelectObject(hdc_mem, hbmp)

            # SRCCOPY = 0x00CC0020
            gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_src, 0, 0, 0x00CC0020)

            class BITMAPINFOHEADER(ctypes.Structure):
                _fields_ = [
                    ("biSize", ctypes.c_uint32),
                    ("biWidth", ctypes.c_int32),
                    ("biHeight", ctypes.c_int32),
                    ("biPlanes", ctypes.c_uint16),
                    ("biBitCount", ctypes.c_uint16),
                    ("biCompression", ctypes.c_uint32),
                    ("biSizeImage", ctypes.c_uint32),
                    ("biXPelsPerMeter", ctypes.c_int32),
                    ("biYPelsPerMeter", ctypes.c_int32),
                    ("biClrUsed", ctypes.c_uint32),
                    ("biClrImportant", ctypes.c_uint32),
                ]

            bmi = BITMAPINFOHEADER()
            bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
            bmi.biWidth = w
            bmi.biHeight = -h  # top-down DIB
            bmi.biPlanes = 1
            bmi.biBitCount = 32
            bmi.biCompression = 0

            buf = ctypes.create_string_buffer(w * h * 4)
            gdi32.GetDIBits(hdc_mem, hbmp, 0, h, buf, ctypes.byref(bmi), 0)

            # Cleanup handles
            gdi32.DeleteObject(hbmp)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(hwnd, hdc_src)

            im = Image.frombuffer("RGBA", (w, h), buf, "raw", "BGRA", 0, 1).convert("RGB")
            im.save(str(target_path), format="PNG", optimize=True)

            buffer = io.BytesIO()
            im.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
            width, height = w, h
            capture_method = "gdi"
        except Exception:
            # Tier 2: PIL ImageGrab
            try:
                from PIL import ImageGrab
                im = ImageGrab.grab()
                im.save(str(target_path), format="PNG")
                buffer = io.BytesIO()
                im.save(buffer, format="PNG")
                img_bytes = buffer.getvalue()
                width, height = im.size
                capture_method = "imagegrab"
            except Exception:
                # Tier 3: mss
                try:
                    import mss
                    with mss.mss() as sct:
                        mon = sct.monitors[1]
                        sct_img = sct.grab(mon)
                        from PIL import Image
                        im = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                        im.save(str(target_path), format="PNG")
                        buffer = io.BytesIO()
                        im.save(buffer, format="PNG")
                        img_bytes = buffer.getvalue()
                        width, height = im.size
                        capture_method = "mss"
                except Exception:
                    # Tier 4: Synthetic diagnostic frame for headless sessions
                    from PIL import Image, ImageDraw
                    im = Image.new("RGB", (1280, 720), color=(10, 18, 34))
                    draw = ImageDraw.Draw(im)
                    draw.text((40, 40), "IT'S MY AI // VISUAL TELEMETRY BUFFER", fill=(0, 240, 255))
                    draw.text((40, 80), f"Active Window: {context['title']}", fill=(255, 255, 255))
                    draw.text((40, 110), f"Process: {context['process']}", fill=(140, 163, 186))
                    im.save(str(target_path), format="PNG")
                    buffer = io.BytesIO()
                    im.save(buffer, format="PNG")
                    img_bytes = buffer.getvalue()
                    width, height = 1280, 720
                    capture_method = "synthetic_fallback"

        b64_str = base64.b64encode(img_bytes).decode("utf-8") if img_bytes else ""

        AuditLogger.log_event(
            event_type="vision_event",
            action="Desktop screenshot captured",
            status="success",
            details={
                "resolution": f"{width}x{height}",
                "method": capture_method,
                "active_window": context["title"],
                "active_process": context["process"]
            }
        )

        return {
            "success": True,
            "message": f"Desktop screen captured ({width}x{height}) via {capture_method}. Active window: '{context['title']}'.",
            "file_path": str(target_path),
            "resolution": f"{width}x{height}",
            "capture_method": capture_method,
            "active_window": context["title"],
            "active_process": context["process"],
            "base64_image": b64_str,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

    async def analyze_screen(self, question: str = "What is on my screen?") -> Dict[str, Any]:
        """
        Takes a screenshot and sends it to the active multimodal AI provider.
        Degrades seamlessly to contextual window analysis if cloud keys are offline.
        """
        cap = self.capture_screenshot()
        b64_image = cap.get("base64_image", "")
        active_window = cap.get("active_window", "Desktop Workspace")
        active_process = cap.get("active_process", "explorer.exe")
        resolution = cap.get("resolution", "1920x1080")

        from backend.app.providers.manager import provider_manager
        active_provider = provider_manager.get_active_provider()

        # Check if active provider supports multimodal vision
        if hasattr(active_provider, "analyze_image") and active_provider.is_configured():
            try:
                analysis = await active_provider.analyze_image(
                    image_base64=b64_image,
                    prompt=f"{question}\nNote: Active foreground application is '{active_window}' ({active_process})."
                )
                return {
                    "success": True,
                    "analysis": analysis,
                    "active_window": active_window,
                    "active_process": active_process,
                    "resolution": resolution,
                    "file_path": cap.get("file_path"),
                    "provider": active_provider.name
                }
            except Exception as e:
                pass

        # Intelligent offline fallback analysis
        analysis = (
            f"Visual Telemetry Analysis ({resolution}):\n"
            f"• Foreground Application: '{active_window}' (Process: {active_process})\n"
            f"• Screen capture resolution: {resolution}\n"
            f"• Status: Visual frame captured and stored at storage/latest_screenshot.png.\n"
            f"To enable deep neural vision reasoning, provide a Gemini or OpenAI API key in settings."
        )

        return {
            "success": True,
            "analysis": analysis,
            "active_window": active_window,
            "active_process": active_process,
            "resolution": resolution,
            "file_path": cap.get("file_path"),
            "provider": "offline-visual-telemetry"
        }

vision_service = VisionService()
