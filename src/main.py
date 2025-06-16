# main.py
import asyncio
import logging
import os
from datetime import datetime
import argparse
from concurrent.futures import ThreadPoolExecutor

from .translator import Translator
from .tts_generator import TTSGenerator
from .audio_player import AudioPlayer
from .text_processor import TextProcessor
from .file_manager import FileManager
from . import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TTSApplication:
    def __init__(self):
        self.translator = Translator()
        self.tts_generator = TTSGenerator()
        self.audio_player = AudioPlayer()
        self.text_processor = TextProcessor()
        self.file_manager = FileManager()

    async def process_chunk(self, chunk: str, output_file: str, chunk_text_file: str, play_queue: asyncio.Queue) -> None:
        tts_file, text_file = await self.tts_generator.generate_tts(chunk, output_file, chunk_text_file)
        if tts_file:
            await play_queue.put([tts_file, text_file])

    async def play_audio_worker(self, play_queue: asyncio.Queue) -> None:
        while True:
            audio_file, text_file = await play_queue.get()
            if audio_file is None:
                break
            with ThreadPoolExecutor() as executor:
                await asyncio.get_event_loop().run_in_executor(executor, self.audio_player.play_audio, audio_file, text_file)
            play_queue.task_done()

    async def talk(self, text: str, output_file: str) -> None:
        try:
            chunks = self.text_processor.split_text_into_chunks(text)
            play_queue = asyncio.Queue()
            play_task = asyncio.create_task(self.play_audio_worker(play_queue))

            for i, chunk in enumerate(chunks):
                chunk_output_file = f"{output_file}_{i}.wav"
                chunk_text_file = f"{output_file}_{i}.txt"
                await self.process_chunk(chunk, chunk_output_file, chunk_text_file, play_queue)

            await play_queue.put([None, None])  # Signal to stop the play_audio_worker
            await play_task

        except Exception as e:
            logger.error(f"An error occurred during TTS and playback: {e}")

    async def run(self, input_text: str = None, is_file: bool = False):
        self.file_manager.create_output_directory(config.OUTPUT_DIRECTORY)

        if input_text is None:
            # Default behavior: use INPUT_FILE from config
            self.translator.translate_file(config.INPUT_FILE, config.TRANSLATED_FILE)
            with open(config.TRANSLATED_FILE, "r", encoding="utf-8") as file:
                text = file.read().strip()
        elif is_file:
            self.translator.translate_file(input_text, config.TRANSLATED_FILE)
            with open(config.TRANSLATED_FILE, "r", encoding="utf-8") as file:
                text = file.read().strip()
        else:
            text = self.translator.translate_text(input_text)

        output_file = None
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            output_file = os.path.join(config.OUTPUT_DIRECTORY, f"output_{timestamp}")
            await self.talk(text, output_file)
        except FileNotFoundError:
            logger.error("Input file not found.")
            empty_output_file = os.path.join(config.OUTPUT_DIRECTORY, "empty")
            await self.talk("I have no idea what to say", empty_output_file)
            output_file = empty_output_file
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        finally:
            if output_file is not None:
                if output_file is not None:
                    self.file_manager.cleanup_temp_files(output_file)

def main():
    parser = argparse.ArgumentParser(description="Text-to-Speech CLI tool")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-f", "--file", help="Input file path")
    group.add_argument("-t", "--text", help="Input text")

    args = parser.parse_args()

    app = TTSApplication()

    if args.file:
        asyncio.run(app.run(args.file, is_file=True))
    elif args.text:
        asyncio.run(app.run(args.text, is_file=False))
    else:
        # No arguments provided, run with default behavior
        asyncio.run(app.run())

if __name__ == "__main__":
    main()
