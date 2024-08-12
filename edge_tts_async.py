import asyncio
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import pygame
import edge_tts

# Constants
INPUT_FILE = "input.txt"
OUTPUT_DIRECTORY = "output_files"
SPECIAL_CHARACTERS = ".!?;"
VOICE = "en-GB-SoniaNeural"
DELIMITER = ":"

def play_audio(audio_file, text_file):
    """Play audio file and display synchronized text."""
    try:
        word_boundaries = load_word_boundaries(text_file)
        
        pygame.mixer.init()
        sound = pygame.mixer.Sound(audio_file)
        sound.play()
        
        start_time = pygame.time.get_ticks() / 1000
        while pygame.mixer.get_busy():
            current_time = pygame.time.get_ticks() / 1000
            elapsed_time = current_time - start_time
            
            display_synchronized_text(word_boundaries, elapsed_time)
            pygame.time.wait(10)  # Short sleep to avoid CPU hogging

    except Exception as e:
        print(f"An error occurred during audio playback: {e}")

def load_word_boundaries(text_file):
    """Load word boundaries from the text file."""
    with open(text_file, "r") as f:
        lines = f.read().split('\n')
    
    word_boundaries = []
    for line in lines:
        parts = line.split(DELIMITER)
        if len(parts) == 3:
            word_boundaries.append([parts[0], float(parts[1]), float(parts[2])])
    
    return word_boundaries

def display_synchronized_text(word_boundaries, elapsed_time):
    """Display text synchronized with audio playback."""
    for word, start, duration in word_boundaries:
        if start <= elapsed_time < (start + duration) and word:
            print(word, end=" ", flush=True)
            word_boundaries[word_boundaries.index([word, start, duration])][0] = ""

async def generate_tts(text, audio_file, text_file):
    """Generate TTS audio and word boundary file."""
    try:
        communicate = edge_tts.Communicate(text, VOICE)
        word_boundaries = []

        with open(audio_file, "wb") as audio_f, open(text_file, "w") as text_f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    word_boundary = f"{chunk['text']}{DELIMITER}{chunk['offset']/10000000}{DELIMITER}{chunk['duration']/10000000}\n"
                    text_f.write(word_boundary)
                    word_boundaries.append(word_boundary)

        return audio_file, text_file
    except Exception as e:
        print(f"An error occurred during TTS generation: {e}")
        return None, None

async def process_chunk(chunk, output_file, chunk_text_file, play_queue):
    """Process a single text chunk."""
    tts_file, text_file = await generate_tts(chunk, output_file, chunk_text_file)
    if tts_file:
        await play_queue.put([tts_file, text_file])

async def play_audio_worker(play_queue):
    """Worker to play audio files from the queue."""
    while True:
        audio_file, text_file = await play_queue.get()
        if audio_file is None:
            break
        with ThreadPoolExecutor() as executor:
            await asyncio.get_event_loop().run_in_executor(executor, play_audio, audio_file, text_file)
        play_queue.task_done()

async def talk(text, output_file):
    """Process the entire text and manage audio playback."""
    try:
        chunks = split_text_into_chunks(text)
        play_queue = asyncio.Queue()
        play_task = asyncio.create_task(play_audio_worker(play_queue))

        for i, chunk in enumerate(chunks):
            chunk_output_file = f"{output_file}_{i}.wav"
            chunk_text_file = f"{output_file}_{i}.txt"
            await process_chunk(chunk, chunk_output_file, chunk_text_file, play_queue)

        await play_queue.put(None)  # Signal to stop the play_audio_worker
        await play_task

    except Exception as e:
        print(f"An error occurred during TTS and playback: {e}")

def split_text_into_chunks(text):
    """Split the input text into chunks based on special characters."""
    chunks = []
    current_chunk = ""
    for char in text:
        current_chunk += char
        if char in SPECIAL_CHARACTERS:
            chunks.append(current_chunk.strip())
            current_chunk = ""
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

async def main():
    """Main function to run the script."""
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as file:
            text = file.read().strip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            output_file = os.path.join(OUTPUT_DIRECTORY, f"output_{timestamp}")
            await talk(text, output_file)
    except FileNotFoundError:
        print(f"Input file '{INPUT_FILE}' not found.")
        await talk(f"i have no idea what to say", os.path.join(OUTPUT_DIRECTORY, f"empty"))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())