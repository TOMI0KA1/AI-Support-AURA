import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import logging
from src.ui.avatars import AvatarState, AvatarManager

logger = logging.getLogger(__name__)

class AuraGUI:
    def __init__(self, aura_app):
        self.aura_app = aura_app
        self.root = tk.Tk()
        self.root.title("Aura Assistant")
        self.root.geometry("300x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c3e50")

        self.avatar_manager = aura_app.avatar
        self.current_state = AvatarState.IDLE

        self._setup_ui()
        self._update_avatar_loop()

    def _setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="AURA", font=("Helvetica", 24, "bold"),
                               fg="#1abc9c", bg="#2c3e50")
        title_label.pack(pady=20)

        # Avatar Image Label
        self.avatar_label = tk.Label(self.root, bg="#2c3e50")
        self.avatar_label.pack(pady=10)

        # Status Label
        self.status_label = tk.Label(self.root, text="Ready, Sir.", font=("Helvetica", 12),
                                     fg="#ecf0f1", bg="#2c3e50")
        self.status_label.pack(pady=10)

        # Action Button (Manual Trigger)
        self.action_btn = ttk.Button(self.root, text="Speak to Aura", command=self.on_btn_click)
        self.action_btn.pack(pady=20)

    def _update_avatar_loop(self):
        state = self.avatar_manager.get_current_state()
        if state != self.current_state:
            self.current_state = state
            self._update_ui_for_state(state)

        self.root.after(500, self._update_avatar_loop)

    def _update_ui_for_state(self, state):
        # SVG is tricky in standard tkinter without extra libs like svglib or cairosvg
        # For simplicity in this environment, we'll just update text until we have a proper image pipeline
        status_texts = {
            AvatarState.IDLE: "Ready, Sir.",
            AvatarState.LISTENING: "Listening...",
            AvatarState.THINKING: "Thinking...",
            AvatarState.SPEAKING: "Responding..."
        }
        self.status_label.config(text=status_texts.get(state, "Ready, Sir."))
        logger.info(f"GUI updated for state: {state}")

    def on_btn_click(self):
        # Trigger command in a separate thread to not freeze UI
        threading.Thread(target=self.aura_app.on_hotkey, daemon=True).start()

    def run(self):
        self.root.mainloop()
