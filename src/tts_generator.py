# tts_generator.py
import edge_tts
from edge_tts import VoicesManager
import random
from typing import Tuple, Optional
import logging
import asyncio
import json
import os
from googletrans import Translator as GoogleTranslator

logger = logging.getLogger(__name__)

from .logging_utils import VERBOSE, vprint
from .settings import settings

class TTSGenerator:
    _voices_cache_file = "voices_cache.json"  # File to store voices

    async def generate_tts(self, text: str, audio_file: str, text_file: str) -> Tuple[Optional[str], Optional[str]]:
        vprint(f"[TTSGenerator] Starting TTS generation for audio file: {audio_file}")
        voice = await self.get_voice(text)
        try:
            vprint(f"[TTSGenerator] Using voice: {voice}")
            communicate = edge_tts.Communicate(text, voice)
            word_boundaries = []

            with open(audio_file, "wb") as audio_f, open(text_file, "w") as text_f:
                async for chunk in communicate.stream():
                    if chunk.get("type") == "audio" and "data" in chunk:
                        audio_f.write(chunk.get("data", b""))
                    elif chunk.get("type") == "WordBoundary":
                        text_val = chunk.get("text")
                        offset_val = chunk.get("offset")
                        duration_val = chunk.get("duration")
                        if text_val is not None and offset_val is not None and duration_val is not None:
                            word_boundary = f"{text_val}:{offset_val/10000000}:{duration_val/10000000}\n"
                            text_f.write(word_boundary)
                            word_boundaries.append(word_boundary)

            vprint(f"[TTSGenerator] Finished TTS generation for: {audio_file}")
            return audio_file, text_file
        except Exception as e:
            logger.error(f"An error occurred during TTS generation: {e}")
            vprint(f"[TTSGenerator] Error during TTS generation for: {audio_file}")
            return None, None

    async def get_voice(self, text: str) -> str:
        # If a default voice is specified in settings, use it
        if settings.tts_voice:
            vprint(f"[TTSGenerator] Using default voice from settings: {settings.tts_voice}")
            return settings.tts_voice

        voices = await self.load_voices_from_file()
        if not voices:
            vprint("[TTSGenerator] Fetching available voices...")
            voices_manager = await VoicesManager.create()
            voices = voices_manager.find()
            await self.save_voices_to_file(voices)
            vprint(f"[TTSGenerator] Fetched and saved {len(voices)} voices.")

        detected_language = self.detect_language(text)
        vprint(f"[TTSGenerator] Detected language: {detected_language}")

        # Filter voices by detected language
        filtered_voices = [voice for voice in voices if voice["Language"] == detected_language]
        if not filtered_voices:
            vprint(f"[TTSGenerator] No voices found for language: {detected_language}. Using default English voices.")
            filtered_voices = voices

        selected_voice = random.choice(filtered_voices)["Name"]
        vprint(f"[TTSGenerator] Selected voice: {selected_voice}")
        return selected_voice

    def detect_language(self, text: str) -> str:
        translator = GoogleTranslator()
        detection = translator.detect(text)
        return detection.lang

    async def save_voices_to_file(self, voices):
        with open(self._voices_cache_file, "w") as f:
            json.dump(voices, f)

    async def load_voices_from_file(self):
        if os.path.exists(self._voices_cache_file):
            with open(self._voices_cache_file, "r") as f:
                return json.load(f)
        return None

if __name__ == "__main__":
    async def main():
        generator = TTSGenerator()
        text = "This is a test of the TTS generator."
        audio_file = "test_audio.wav"
        text_file = "test_text.txt"

        result = await generator.generate_tts(text, audio_file, text_file)
        if result:
            print(f"TTS generated successfully. Audio file: {audio_file}, Text file: {text_file}")
        else:
            print("TTS generation failed.")

    asyncio.run(main())
