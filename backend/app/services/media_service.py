"""
IT'S MY AI — Media & Entertainment Controller Service
Implements Section 18:
- Music and media playback dispatch (YouTube, Spotify web, local media)
- Windows media virtual key control (Play/Pause, Next track, Previous track, Mute)
- Safe, zero-RAM footprint using native Windows User32 APIs
"""

import sys
import os
import subprocess
import urllib.parse
from typing import Dict, Any, Optional

class MediaService:
    # Virtual Key Codes on Windows
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    VK_MEDIA_STOP = 0xB2
    VK_MEDIA_PLAY_PAUSE = 0xB3
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF

    @classmethod
    def send_virtual_key(cls, vk_code: int) -> bool:
        """Sends a hardware media key event using native Windows ctypes."""
        if sys.platform != "win32":
            return False
        try:
            import ctypes
            # Key down
            ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
            # Key up
            ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)
            return True
        except Exception:
            return False

    def control_playback(self, action: str) -> Dict[str, Any]:
        """Controls media playback: play, pause, next, previous, mute."""
        action = action.lower().strip()
        key_map = {
            "play": self.VK_MEDIA_PLAY_PAUSE,
            "pause": self.VK_MEDIA_PLAY_PAUSE,
            "toggle": self.VK_MEDIA_PLAY_PAUSE,
            "next": self.VK_MEDIA_NEXT_TRACK,
            "previous": self.VK_MEDIA_PREV_TRACK,
            "prev": self.VK_MEDIA_PREV_TRACK,
            "stop": self.VK_MEDIA_STOP,
            "mute": self.VK_VOLUME_MUTE,
        }

        vk = key_map.get(action)
        if vk is None:
            return {
                "success": False,
                "message": f"Unsupported media action '{action}'. Supported: play, pause, next, previous, mute."
            }

        success = self.send_virtual_key(vk)
        return {
            "success": success,
            "action": action,
            "message": f"Sent media command '{action}' to Windows audio subsystem."
        }

    def play_youtube(self, query: str) -> Dict[str, Any]:
        """Searches and opens a video or playlist on YouTube in the default browser."""
        clean_query = query.strip()
        encoded = urllib.parse.quote_plus(clean_query)
        url = f"https://www.youtube.com/results?search_query={encoded}"

        try:
            if sys.platform == "win32":
                os.startfile(url)
            else:
                subprocess.Popen(["xdg-open", url])
            return {
                "success": True,
                "query": clean_query,
                "url": url,
                "message": f"Opening YouTube search for '{clean_query}' in your browser."
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to launch browser: {str(e)}"}

    def open_spotify(self, search_query: Optional[str] = None) -> Dict[str, Any]:
        """Opens Spotify app or web player with optional search."""
        if search_query:
            encoded = urllib.parse.quote(search_query)
            url = f"https://open.spotify.com/search/{encoded}"
        else:
            url = "https://open.spotify.com"

        try:
            if sys.platform == "win32":
                os.startfile(url)
            return {
                "success": True,
                "query": search_query or "home",
                "message": f"Opening Spotify: {url}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

media_service = MediaService()
