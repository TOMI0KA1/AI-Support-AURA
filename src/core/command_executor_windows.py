"""Windows-specific command executor
"""
import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    HAS_PYCAW = True
except ImportError:
    HAS_PYCAW = False
    logger.warning("pycaw or comtypes not found. Volume control will use fallback if available.")

SYSTEM_DIRS = [
    os.environ.get('WINDIR', r"C:\Windows"),
    os.environ.get('SystemRoot', r"C:\Windows"),
]

def get_system_time() -> str:
    now = datetime.now()
    return now.strftime("%H:%M")

def get_weather(city: str = "") -> str:
    try:
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        return "Не удалось получить данные о погоде."
    except Exception:
        logger.exception("Error fetching weather")
        return "Ошибка при получении погоды."

def set_volume(level: int) -> bool:
    """Sets system volume (0-100)"""
    if not HAS_PYCAW:
        logger.warning("Volume control failed: pycaw not installed")
        return False
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        # level is 0-100, pycaw expects 0.0-1.0
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        return True
    except Exception:
        logger.exception("Error setting volume")
        return False

def open_path(path: str) -> bool:
    try:
        if path.startswith(("http://", "https://")):
            os.startfile(path)
            return True
        p = Path(path)
        if p.exists():
            os.startfile(str(p))
            return True
        subprocess.Popen(path, shell=True)
        return True
    except Exception:
        logger.exception("Error opening path")
        return False

def is_path_allowed(path: str) -> bool:
    try:
        p = Path(path).resolve()
        for sd in SYSTEM_DIRS:
            if str(p).lower().startswith(str(Path(sd).resolve()).lower()):
                logger.warning("Access to system folder blocked")
                return False
        return True
    except Exception:
        logger.exception("Path validation error")
        return False
