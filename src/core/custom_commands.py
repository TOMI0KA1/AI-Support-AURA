"""
Менеджер пользовательских команд для Aura
Позволяет привязывать фразы-триггеры к открытию файлов/папок/ссылок
"""

import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CustomCommandsManager:
    def __init__(self, filepath="data/custom_commands.json"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.commands = {}
        self.load_commands()

    def load_commands(self):
        try:
            if self.filepath.exists():
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.commands = json.load(f)
                logger.info(f"Loaded {len(self.commands)} custom commands")
            else:
                self.commands = {}
        except Exception:
            logger.exception("Failed to load custom commands")
            self.commands = {}

    def save_commands(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.commands, f, ensure_ascii=False, indent=4)
            logger.info("Saved custom commands")
        except Exception:
            logger.exception("Failed to save custom commands")

    def add_command(self, phrase: str, path: str):
        self.commands[phrase.lower().strip()] = path
        self.save_commands()

    def get_path_for_command(self, command: str) -> str:
        cmd_lower = command.lower().strip()
        # Поиск точного совпадения или вхождения триггера в команду
        for phrase, path in self.commands.items():
            if phrase in cmd_lower:
                return path
        return None
