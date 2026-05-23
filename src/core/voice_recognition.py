"""
Voice recognition module for Aura using SpeechRecognition library.
"""
import speech_recognition as sr
import logging

logger = logging.getLogger(__name__)

class VoiceRecognizer:
    def __init__(self, language: str = "ru-RU"):
        self.recognizer = sr.Recognizer()
        self.language = language
        self.microphone = sr.Microphone()

        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        logger.info("VoiceRecognizer initialized and calibrated")

    def listen(self) -> str:
        """
        Listens for a command and returns the recognized text.
        """
        with self.microphone as source:
            logger.info("Listening...")
            audio = self.recognizer.listen(source)

        try:
            logger.info("Recognizing...")
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.info(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Could not request results from service; {e}")
            return ""

    def listen_in_background(self, callback):
        """
        Starts listening in the background and calls the callback when a command is recognized.
        """
        stop_listening = self.recognizer.listen_in_background(self.microphone, callback)
        return stop_listening
