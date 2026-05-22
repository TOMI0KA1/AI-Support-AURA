"""Windows TTS через pyttsx3 (SAPI5)
"""
import pyttsx3
import logging
import threading

logger = logging.getLogger(__name__)

class VoiceEngineWindows:
    def __init__(self, voice_name: str = None, rate: int = 170, volume: float = 1.0):
        try:
            self.engine = pyttsx3.init('sapi5')
        except Exception:
            self.engine = pyttsx3.init()
        self.rate = rate
        self.volume = max(0.0, min(1.0, volume))
        self.voice_name = voice_name
        self._configure()

    def _configure(self):
        try:
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            voices = self.engine.getProperty('voices')
            if self.voice_name:
                for v in voices:
                    if self.voice_name.lower() in v.name.lower():
                        self.engine.setProperty('voice', v.id)
                        logger.info(f"Selected voice: {v.name}")
                        break
            else:
                for v in voices:
                    langs = []
                    try:
                        langs = [l.decode('utf-8') if isinstance(l, bytes) else str(l) for l in v.languages]
                    except Exception:
                        langs = []
                    if any('ru' in l.lower() for l in langs):
                        self.engine.setProperty('voice', v.id)
                        logger.info(f"Selected RU voice: {v.name}")
                        break
        except Exception:
            logger.exception("Error configuring TTS")

    def speak(self, text: str, async_mode: bool = True):
        if not text:
            return False
        try:
            self.engine.say(text)
            if async_mode:
                threading.Thread(target=self.engine.runAndWait, daemon=True).start()
            else:
                self.engine.runAndWait()
            return True
        except Exception:
            logger.exception("TTS speak error")
            return False

    def save_to_file(self, text: str, filepath: str):
        try:
            self.engine.save_to_file(text, filepath)
            self.engine.runAndWait()
            return True
        except Exception:
            logger.exception("Error saving TTS to file")
            return False
