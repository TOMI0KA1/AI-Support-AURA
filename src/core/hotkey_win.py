"""Hotkey listener using Win32 RegisterHotKey (pywin32). Uses Alt+A by default.
"""
import threading
import logging

logger = logging.getLogger(__name__)

try:
    import win32con
    import win32gui
    from ctypes import windll
except Exception:
    win32con = None
    win32gui = None
    windll = None
    logger.warning("pywin32 not available: Hotkey will be disabled")

MODS = {
    'alt': 0x0001,
    'ctrl': 0x0002,
    'shift': 0x0004,
    'win': 0x0008
}

class HotkeyListener(threading.Thread):
    def __init__(self, modifiers=('alt',), key='a', callback=None, id=1):
        super().__init__(daemon=True)
        self.mod = sum(MODS.get(m, 0) for m in modifiers)
        self.vk = ord(key.upper())
        self.callback = callback
        self.id = id
        self.hwnd = None
        self.running = False

    def run(self):
        if not win32gui or not windll:
            logger.error("HotkeyListener unavailable (pywin32 missing)")
            return

        message_map = {win32con.WM_HOTKEY: self._on_hotkey}
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = message_map
        wc.lpszClassName = "AuraHotkeyListenerClass"
        class_atom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(wc.lpszClassName, "AuraHotkeyListener", 0, 0, 0, 0, 0, 0, 0, None)
        if not windll.user32.RegisterHotKey(self.hwnd, self.id, self.mod, self.vk):
            logger.error("Failed to register hotkey. Try running with elevated privileges.")
            return
        self.running = True
        logger.info("Hotkey registered")
        try:
            while self.running:
                win32gui.PumpWaitingMessages()
        finally:
            try:
                windll.user32.UnregisterHotKey(self.hwnd, self.id)
                win32gui.DestroyWindow(self.hwnd)
            except Exception:
                pass

    def _on_hotkey(self, hwnd, msg, wparam, lparam):
        logger.info("Hotkey pressed")
        if callable(self.callback):
            try:
                self.callback()
            except Exception:
                logger.exception("Error in hotkey callback")
