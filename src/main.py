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
from .file_manager import UnifiedFileManager
from .settings import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from .logging_utils import vprint
from . import logging_utils

class TTSApplication:
    def __init__(self):
        vprint("[TTSApplication] Initializing components...")
        self.translator = Translator()
        self.tts_generator = TTSGenerator()
        self.audio_player = AudioPlayer()
        self.text_processor = TextProcessor()
        self.file_manager = UnifiedFileManager(settings.output_directory)
        vprint("[TTSApplication] Initialization complete.")

    async def process_chunk(self, chunk: str, output_file: str, chunk_text_file: str, play_queue: asyncio.Queue) -> None:
        vprint(f"[TTSApplication] Generating TTS for chunk: {output_file}")
        tts_file, text_file = await self.tts_generator.generate_tts(chunk, output_file, chunk_text_file)
        if tts_file:
            vprint(f"[TTSApplication] TTS generated: {tts_file}")
            await play_queue.put([tts_file, text_file])

    async def play_audio_worker(self, play_queue: asyncio.Queue) -> None:
        vprint("[TTSApplication] Audio playback worker started.")
        while True:
            item = await play_queue.get()
            audio_file, text_file = item[0], item[1]
            if audio_file is None:
                vprint("[TTSApplication] Audio playback worker stopping.")
                break
            vprint(f"[TTSApplication] Playing audio: {audio_file}")
            with ThreadPoolExecutor() as executor:
                await asyncio.get_event_loop().run_in_executor(executor, self.audio_player.play_audio, audio_file, text_file)
            play_queue.task_done()

    async def talk(self, text: str, output_file: str) -> None:
        try:
            vprint("[TTSApplication] Splitting text into chunks for TTS...")
            chunks = self.text_processor.split_text_into_chunks(text)
            vprint(f"[TTSApplication] {len(chunks)} chunk(s) to process for TTS.")
            play_queue = asyncio.Queue()
            play_task = asyncio.create_task(self.play_audio_worker(play_queue))

            for i, chunk in enumerate(chunks):
                chunk_output_file = f"{output_file}_{i}.wav"
                chunk_text_file = f"{output_file}_{i}.txt"
                vprint(f"[TTSApplication] Processing chunk {i+1}/{len(chunks)}")
                await self.process_chunk(chunk, chunk_output_file, chunk_text_file, play_queue)

            await play_queue.put([None, None])  # Signal to stop the play_audio_worker
            await play_task
            vprint("[TTSApplication] All chunks processed and played.")

        except Exception as e:
            logger.error(f"An error occurred during TTS and playback: {e}")

    async def run(self, input_text: str | None = None, is_file: bool = False, target_language: str | None = None):
        vprint("[TTSApplication] Unified file manager ready...")
        # The unified file manager automatically sets up directories

        # Step 1: Input Handling and Translation
        if input_text is None:
            vprint("[TTSApplication] No input provided. Using default input file.")
            try:
                with open(settings.input_file, "r", encoding="utf-8") as file:
                    original_text = file.read().strip()
            except FileNotFoundError:
                original_text = "there is no input file"
        elif is_file:
            vprint(f"[TTSApplication] Reading input from file: {input_text}")
            with open(input_text, "r", encoding="utf-8") as file:
                original_text = file.read().strip()
        else:
            vprint("[TTSApplication] Using provided input text.")
            original_text = input_text

        # Only translate if target_language is set and not empty
        if target_language:
            vprint(f"[TTSApplication] Translating input text to '{target_language}'...")
            translated_text = self.translator.translate_text(original_text, target_language=target_language)
        else:
            vprint("[TTSApplication] No translation requested. Using original text.")
            translated_text = original_text

        # Step 2: Text Processing (split into chunks)
        vprint("[TTSApplication] Splitting translated text into chunks...")
        chunks = self.text_processor.split_text_into_chunks(translated_text)

        # Step 2b: Reconstruct translated file from chunks
        reconstructed_translated_text = "".join(chunks)

        # Use unified file manager for translation file
        if target_language:
            translation_file = self.file_manager.create_translation_file_path("auto", target_language)
        else:
            translation_file = self.file_manager.create_translation_file_path("auto", "auto")

        vprint(f"[TTSApplication] Writing translated text to file: {translation_file}")
        with open(translation_file, "w", encoding="utf-8") as f:
            f.write(reconstructed_translated_text)

        output_file = None
        try:
            # Use unified file manager for audio output
            base_audio_file, _ = self.file_manager.create_audio_file_path("cli_output")
            output_file = base_audio_file.replace(".wav", "")  # Remove extension for base name
            vprint(f"[TTSApplication] Starting TTS and playback. Output base: {output_file}")
            await self.talk(reconstructed_translated_text, output_file)
        except FileNotFoundError:
            logger.error("Input file not found.")
            empty_audio_file, _ = self.file_manager.create_audio_file_path("empty")
            empty_output_file = empty_audio_file.replace(".wav", "")
            await self.talk("I have no idea what to say", empty_output_file)
            output_file = empty_output_file
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        finally:
            if output_file is not None:
                vprint(f"[TTSApplication] Cleaning up session files...")
                cleanup_count = self.file_manager.cleanup_session_files()
                vprint(f"[TTSApplication] Cleaned up {cleanup_count} files.")

def main():
    parser = argparse.ArgumentParser(
        description="Text-to-Speech CLI tool with web server capability",
        epilog="""
Examples:
  # CLI mode (default)
  %(prog)s -t "Hello world"
  %(prog)s -f input.txt --language en

  # Web server mode
  %(prog)s --server
  %(prog)s --server --host 0.0.0.0 --port 8080
  %(prog)s --server --reload --verbose
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # CLI mode arguments
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-f", "--file", help="Input file path")
    group.add_argument("-t", "--text", help="Input text")
    parser.add_argument("-l", "--language", help="Target language for translation (if not set, no translation will be performed)", default=None)

    # Server mode arguments
    parser.add_argument("--server", action="store_true", help="Run the web server instead of CLI mode")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (only used with --server)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (only used with --server)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development (only used with --server)")

    # Common arguments
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args, remaining_args = parser.parse_known_args()
    logging_utils.VERBOSE = args.verbose

    # Validate arguments
    if not args.server and (args.host != "127.0.0.1" or args.port != 8000 or args.reload):
        parser.error("--host, --port, and --reload can only be used with --server")

    if args.server and (args.file or args.text):
        parser.error("Cannot use --file or --text with --server mode")

    if args.server:
        vprint("[Main] Starting web server...")
        # Pass server-specific arguments to web_server.main()
        import sys
        server_args = [sys.argv[0]]
        if args.host != "127.0.0.1":
            server_args.extend(["--host", args.host])
        if args.port != 8000:
            server_args.extend(["--port", str(args.port)])
        if args.reload:
            server_args.append("--reload")
        if args.verbose:
            server_args.extend(["--log-level", "debug"])

        # Add any remaining arguments
        server_args.extend(remaining_args)

        sys.argv = server_args
        from . import web_server
        web_server.main()
    else:
        vprint("[Main] Initializing TTSApplication...")
        app = TTSApplication()

        # If language flag is set to empty string, treat as no translation
        target_language = args.language if args.language else None

        if args.file:
            vprint(f"[Main] File input mode. File: {args.file}")
            asyncio.run(app.run(args.file, is_file=True, target_language=target_language))
        elif args.text:
            vprint("[Main] Text input mode.")
            asyncio.run(app.run(args.text, is_file=False, target_language=target_language))
        else:
            vprint("[Main] No input provided. Using default behavior.")
            asyncio.run(app.run(target_language=target_language))

if __name__ == "__main__":
    main()
