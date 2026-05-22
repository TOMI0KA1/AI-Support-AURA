"""Главный лаунчер Aura (Windows-оптимизированный)
"""
import logging
import os
import sys
import time
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('aura')

try:
    from src.core.optimized_ai_processor import OptimizedAI
    from src.core.voice_engine_windows import VoiceEngineWindows
    from src.core.tts_cache import speak_with_cache
    from src.core.memory_monitor import MemoryMonitor
    from src.core.hotkey_win import HotkeyListener
    from src.core.command_executor_windows import open_path, is_path_allowed
    from src.ml.adaptive_learning import AdaptiveLearningSystem
    from src.ui.avatars import AvatarManager, AvatarState
    from src.core.custom_commands import CustomCommandsManager
except Exception:
    logger.exception('Failed to import internal modules')
    raise

class AuraApp:
    def __init__(self, memory_limit_mb: int = 1200):
        self.logger = logging.getLogger('AuraApp')
        self.ai = OptimizedAI()
        self.voice = VoiceEngineWindows()
        self.memory_monitor = MemoryMonitor(self, max_rss_mb=memory_limit_mb)
        self.hotkey = None
        self.avatar = AvatarManager()
        self.learning_system = AdaptiveLearningSystem(ai_processor=self.ai)
        self.custom_commands = CustomCommandsManager()
        logger.info('AuraApp initialized')

    def start(self):
        logger.info('Starting AuraApp...')
        self.avatar.set_state(AvatarState.IDLE)
        self.memory_monitor.start()
        try:
            self.hotkey = HotkeyListener(modifiers=('alt',), key='a', callback=self.on_hotkey)
            self.hotkey.start()
        except Exception:
            logger.exception('Failed to init hotkey')
        logger.info('Aura running. Press Alt+A to activate (if supported)')

    def on_hotkey(self):
        logger.info('Hotkey activated — simulating command')
        cmd = 'Aura открой блокнот'
        response = self.process_command(cmd)
        logger.info(f'Aura responded: {response}')

    def process_command(self, command: str) -> str:
        cleaned_cmd = command.strip().lower()
        wake_words = ["aura", "аура"]
        has_wake_word = False
        task = command
        
        for w in wake_words:
            if cleaned_cmd.startswith(w):
                has_wake_word = True
                task = command[len(w):].strip()
                break
        
        if has_wake_word:
            logger.info("Wake word detected! Replying 'Yes, sir'.")
            self.avatar.set_state(AvatarState.LISTENING)
            try:
                # Speak "Да, сэр" first
                self.voice.speak("Да, сэр", async_mode=False)
            except Exception:
                logger.exception("Failed to speak 'Да, сэр'")
        
        start_time = time.time()
        self.avatar.set_state(AvatarState.THINKING)
        
        # Check if user wants to register a custom command
        add_match_ru = re.match(r"(?:добавь команду|запиши команду)\s+(.+?)\s+(?:для файла|файл|открывать)\s+(.+)", task, re.IGNORECASE)
        add_match_en = re.match(r"(?:add command|register command)\s+(.+?)\s+(?:for file|file|open)\s+(.+)", task, re.IGNORECASE)
        
        match = add_match_ru or add_match_en
        if match:
            trigger_phrase = match.group(1).strip()
            file_path = match.group(2).strip().strip('"').strip("'")
            self.custom_commands.add_command(trigger_phrase, file_path)
            resp = f"Команда '{trigger_phrase}' успешно добавлена для открытия файла '{file_path}'."
            self.avatar.set_state(AvatarState.SPEAKING)
            try:
                speak_with_cache(resp, self.voice, voice_name='default')
            except Exception:
                self.voice.speak(resp)
            self.avatar.set_state(AvatarState.IDLE)
            return resp

        # Check custom commands first
        custom_path = self.custom_commands.get_path_for_command(task)
        if custom_path:
            logger.info(f"Custom command matched! Opening path: {custom_path}")
            success = self.open_file_or_app(custom_path)
            if success:
                resp = f"Открываю файл по вашей команде."
            else:
                resp = f"Не удалось открыть файл {custom_path}."
            
            self.avatar.set_state(AvatarState.SPEAKING)
            try:
                speak_with_cache(resp, self.voice, voice_name='default')
            except Exception:
                self.voice.speak(resp)
                
            duration = time.time() - start_time
            self.learning_system.train_on_command(task, resp, success=success, response_time=duration)
            self.avatar.set_state(AvatarState.IDLE)
            return resp

        # Fallback: process command through AI Adapter
        response = self.ai.process_command(task)
        self.avatar.set_state(AvatarState.SPEAKING)
        try:
            speak_with_cache(response, self.voice, voice_name='default')
        except Exception:
            logger.exception('TTS playback failed — fallback to direct speak')
            try:
                self.voice.speak(response)
            except Exception:
                pass
        
        duration = time.time() - start_time
        # Train the adaptive learning system on the processed command
        self.learning_system.train_on_command(task, response, success=True, response_time=duration)
        self.avatar.set_state(AvatarState.IDLE)
        return response

    def open_file_or_app(self, path: str) -> bool:
        if not is_path_allowed(path):
            logger.warning('Blocked attempt to open restricted path')
            return False
        return open_path(path)

    def on_memory_pressure(self):
        logger.info('Memory pressure — delegating to AI module')
        try:
            self.ai.on_memory_pressure()
        except Exception:
            logger.exception('Error in on_memory_pressure')

    def shutdown(self):
        logger.info('Shutting down AuraApp...')
        try:
            if self.hotkey:
                self.hotkey.running = False
            self.memory_monitor.stop()
        except Exception:
            pass

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ('--test', '-t', '--test-only'):
        from src.core.built_in_tester import run_all_tests
        success = run_all_tests()
        sys.exit(0 if success else 1)
        
    app = AuraApp(memory_limit_mb=1200)
    app.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        app.shutdown()

if __name__ == '__main__':
    main()

