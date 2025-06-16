# audio_player.py
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from typing import List
import logging


logger = logging.getLogger(__name__)

class AudioPlayer:
    def play_audio(self, audio_file: str, text_file: str) -> None:
        try:
            word_boundaries = self.load_word_boundaries(text_file)

            pygame.mixer.init()
            sound = pygame.mixer.Sound(audio_file)
            sound.play()

            start_time = pygame.time.get_ticks() / 1000
            while pygame.mixer.get_busy():
                current_time = pygame.time.get_ticks() / 1000
                elapsed_time = current_time - start_time

                self.display_synchronized_text(word_boundaries, elapsed_time)
                pygame.time.wait(10)  # Short sleep to avoid CPU hogging

        except Exception as e:
            logger.error(f"An error occurred during audio playback: {e}")

    def load_word_boundaries(self, text_file: str) -> List[List[str]]:
        with open(text_file, "r") as f:
            lines = f.read().split('\n')

        word_boundaries = []
        for line in lines:
            parts = line.split(':')
            if len(parts) == 3:
                word_boundaries.append([parts[0], float(parts[1]), float(parts[2])])

        return word_boundaries

    def display_synchronized_text(self, word_boundaries: List[List[str]], elapsed_time: float) -> None:
        for word, start, duration in word_boundaries:
            try:
                start_f = float(start)
                duration_f = float(duration)
            except (ValueError, TypeError):
                continue
            if start_f <= elapsed_time < (start_f + duration_f) and word:
                print(word, end=" ", flush=True)
                word_boundaries[word_boundaries.index([word, start, duration])][0] = ""

if __name__ == "__main__":
    # This assumes you have generated audio and text files using the TTS generator
    audio_file = "test_audio.wav"
    text_file = "test_text.txt"

    player = AudioPlayer()
    print("Playing audio with synchronized text:")
    player.play_audio(audio_file, text_file)

    # Clean up pygame
    pygame.mixer.quit()
