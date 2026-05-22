"""Кеш TTS на диск для Windows.
Использует save_to_file у pyttsx3, если доступно. Иначе fallback на speak.
"""
import hashlib
from pathlib import Path
import logging
import subprocess
import platform
import time
import os

logger = logging.getLogger(__name__)

TTS_CACHE_DIR = Path("data/tts_cache")
TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _hash_text(text: str, voice: str = "default") -> str:
    return hashlib.sha256(f"{voice}:{text}".encode('utf-8')).hexdigest()

def speak_with_cache(text: str, tts_engine, voice_name: str = "default", async_mode: bool = True) -> bool:
    if not text:
        return False
    key = _hash_text(text, voice_name)
    out_file = TTS_CACHE_DIR / f"{key}.mp3"

    if out_file.exists():
        logger.debug("Playing from TTS cache")
        return _play_file(out_file)

    try:
        if hasattr(tts_engine, 'save_to_file'):
            tts_engine.save_to_file(text, str(out_file))
            tts_engine.runAndWait()
        else:
            logger.debug("TTS engine doesn't support save_to_file; calling speak directly")
            tts_engine.speak(text, async_mode=async_mode)
            return True

        time.sleep(0.05)
        if out_file.exists():
            return _play_file(out_file)
        else:
            logger.warning("TTS file not found after synthesis")
            return False
    except Exception:
        logger.exception("Error generating TTS file")
        return False

def _play_file(path: Path) -> bool:
    try:
        if platform.system() == "Windows":
            os.startfile(str(path))
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return True
    except Exception:
        logger.exception("Error playing file")
        return False
