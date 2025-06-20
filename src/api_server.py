from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
import asyncio

from .settings import settings
from .file_manager import FileManager
from .translator import Translator
from .tts_generator import TTSGenerator

app = FastAPI(
    title="Text-to-Speech API",
    description="API for converting text to speech with optional translation.",
    version="1.0.0",
)

# Use global settings and instantiate components
file_manager = FileManager()
translator = Translator()
tts_generator = TTSGenerator()

class SynthesizeRequest(BaseModel):
    text: str
    language: str | None = None # Target language for translation (e.g., 'en', 'fr')
    voice: str | None = None    # Specific TTS voice to use (e.g., 'en-US-AriaNeural')

async def remove_file_in_background(path: str):
    """Asynchronously removes a file after a short delay to allow client download."""
    await asyncio.sleep(5) # Give client a few seconds to download the file
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"Cleaned up temporary file: {path}")
        except OSError as e:
            print(f"Error cleaning up file {path}: {e}")

@app.post("/synthesize")
async def synthesize_text_to_speech(request: SynthesizeRequest, background_tasks: BackgroundTasks):
    """
    Converts the provided text to speech.
    Optionally translates the text before synthesis.
    The generated audio file is returned directly and then cleaned up.

    **Note:** This implementation assumes that `TTSGenerator.generate_audio_file`
    can accept an `output_filepath` argument to save the generated audio
    to a specific, unique file. If the existing `TTSGenerator` does not support this,
    it would require a modification to `tts/src/tts_generator.py` and potentially
    `tts/src/file_manager.py` to allow dynamic output paths,
    or a different strategy for handling unique files per request.
    """
    try:
        input_text = request.text
        target_language = request.language

        # 1. Translate text if a target language is provided
        if target_language:
            translated_text = translator.translate_text(input_text, target_language)
            if not translated_text:
                raise HTTPException(status_code=500, detail="Translation failed.")
            input_text = translated_text
            print(f"Translated text to '{target_language}': {input_text}")
        else:
            print(f"No translation requested. Original text: {input_text}")

        # 2. Generate TTS audio to a temporary unique file
        # Ensure the output directory exists
        output_dir = settings.output_directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate a unique filename for the temporary audio file
        temp_audio_basename = f"api_tts_output_{uuid.uuid4()}.mp3"
        temp_audio_filepath = os.path.join(output_dir, temp_audio_basename)

        # Generate TTS using the existing generate_tts method
        try:
            # Create temporary text file path for word boundaries
            temp_text_filepath = temp_audio_filepath.replace('.mp3', '.txt')

            # Use existing generate_tts method
            audio_file, text_file = await tts_generator.generate_tts(
                text=input_text,
                audio_file=temp_audio_filepath.replace('.mp3', '.wav'),
                text_file=temp_text_filepath
            )

            if not audio_file:
                raise HTTPException(status_code=500, detail="TTS generation failed")

            # Update the audio filepath to the actual generated file
            temp_audio_filepath = audio_file

        except Exception as e:
            # Clean up any partial files
            for filepath in [temp_audio_filepath, temp_audio_filepath.replace('.mp3', '.wav'), temp_audio_filepath.replace('.mp3', '.txt')]:
                if os.path.exists(filepath):
                    os.remove(filepath)
            raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")

        # Check if file was actually created by TTSGenerator
        if not os.path.exists(temp_audio_filepath):
            raise HTTPException(status_code=500, detail="TTS generation completed, but audio file was not found at expected path.")

        # Return the generated audio file as a FileResponse
        # Determine media type based on actual file extension
        media_type = "audio/wav" if temp_audio_filepath.endswith('.wav') else "audio/mpeg"
        filename = "speech.wav" if temp_audio_filepath.endswith('.wav') else "speech.mp3"

        response = FileResponse(
            path=temp_audio_filepath,
            media_type=media_type,
            filename=filename
        )

        # Add a background task to clean up the temporary file after the response is sent.
        background_tasks.add_task(remove_file_in_background, temp_audio_filepath)

        return response

    except HTTPException:
        # Re-raise FastAPI HTTP exceptions directly
        raise
    except Exception as e:
        # Catch any other unexpected errors and return a 500 status
        print(f"An unexpected error occurred in /synthesize: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")
