# tts_generator.py
import edge_tts
from edge_tts import VoicesManager
import random
from typing import Tuple, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

class TTSGenerator:
    async def generate_tts(self, text: str, audio_file: str, text_file: str) -> Tuple[Optional[str], Optional[str]]:
        voice = await self.get_voice()
        try:
            communicate = edge_tts.Communicate(text, voice)
            word_boundaries = []

            with open(audio_file, "wb") as audio_f, open(text_file, "w") as text_f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_f.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        word_boundary = f"{chunk['text']}:{chunk['offset']/10000000}:{chunk['duration']/10000000}\n"
                        text_f.write(word_boundary)
                        word_boundaries.append(word_boundary)

            return audio_file, text_file
        except Exception as e:
            logger.error(f"An error occurred during TTS generation: {e}")
            return None, None

    async def get_voice(self) -> str:
        voices = await VoicesManager.create()
        voice = voices.find(Language="en")
        return random.choice(voice)["Name"]

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
