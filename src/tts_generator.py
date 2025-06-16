# tts_generator.py
import edge_tts
from edge_tts import VoicesManager
import random
from typing import Tuple, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

from .logging_utils import VERBOSE, vprint

class TTSGenerator:
    async def generate_tts(self, text: str, audio_file: str, text_file: str) -> Tuple[Optional[str], Optional[str]]:
        vprint(f"[TTSGenerator] Starting TTS generation for audio file: {audio_file}")
        voice = await self.get_voice()
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

    async def get_voice(self) -> str:
        vprint("[TTSGenerator] Fetching available voices...")
        voices = await VoicesManager.create()
        voice = voices.find(Language="en")
        selected_voice = random.choice(voice)["Name"]
        vprint(f"[TTSGenerator] Selected voice: {selected_voice}")
        return selected_voice

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
