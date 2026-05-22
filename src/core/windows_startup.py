"""Windows autostart helper via HKCU Run key
"""
import logging
import os
from pathlib import Path
import winreg

logger = logging.getLogger(__name__)
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

def set_autostart(enable: bool, app_name: str = "AuraAssistant", exe_path: str = None) -> bool:
    try:
        exe = exe_path or str(Path(os.path.abspath(__file__)).parents[2] / "dist" / "Aura.exe")
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe}"')
            logger.info(f"Autostart enabled: {exe}")
        else:
            try:
                winreg.DeleteValue(key, app_name)
                logger.info("Autostart disabled")
            except FileNotFoundError:
                logger.info("Autostart entry not found")
        winreg.CloseKey(key)
        return True
    except Exception:
        logger.exception("Error setting autostart")
        return False
