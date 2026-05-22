"""Windows-specific command executor
"""
import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SYSTEM_DIRS = [
    os.environ.get('WINDIR', r"C:\Windows"),
    os.environ.get('SystemRoot', r"C:\Windows"),
]

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
