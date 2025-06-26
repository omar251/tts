from googletrans import Translator as GoogleTranslator

from .logging_utils import VERBOSE, vprint
from .settings import settings

class Translator:
    def __init__(self):
        self.translator = GoogleTranslator()

    def detect_language(self, text: str) -> str:
        """Detect the language of the given text."""
        detection = self.translator.detect(text)
        return detection.lang

    def translate_file(self, input_file: str, output_file: str) -> None:
        vprint(f"[Translator] Reading input file: {input_file}")
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
        vprint("[Translator] Translating file content...")
        translated = self.translate_text(text)
        vprint(f"[Translator] Writing translated content to: {output_file}")
        with open(output_file, "w", encoding='utf-8') as f:
            f.write(translated)

    def translate_text(self, text: str, target_language: str | None = None) -> str:
        """
        Translate text to the target language if specified.
        If target_language is None or empty, return the original text.
        """
        if not target_language:
            vprint("[Translator] No target language set. Skipping translation.")
            return text

        vprint(f"[Translator] Splitting text into chunks for translation to '{target_language}'...")
        # Split text into chunks for translation (configurable size, default 5000)
        max_chars = getattr(settings, 'max_translate_chars', 5000)
        chunks = []
        current = ""
        for line in text.splitlines(keepends=True):
            if len(current) + len(line) > max_chars:
                if current:
                    chunks.append(current)
                    current = ""
            current += line
        if current:
            chunks.append(current)
        vprint(f"[Translator] {len(chunks)} chunk(s) to translate.")
        translated_chunks = []
        for idx, chunk in enumerate([c for c in chunks if c.strip()]):
            vprint(f"[Translator] Translating chunk {idx+1}/{len(chunks)}...")
            try:
                translated_chunk = self.translator.translate(chunk, src='auto', dest=target_language).text
                if translated_chunk is not None:
                    translated_chunks.append(translated_chunk)
                else:
                    vprint(f"[Translator] Warning: Translation for chunk {idx+1} returned None. Appending empty string.")
                    translated_chunks.append("")
            except Exception as e:
                vprint(f"[Translator] Error translating chunk {idx+1}: {e}. Appending original chunk.")
                translated_chunks.append(chunk) # Fallback to original chunk on error
        vprint("[Translator] All chunks translated.")
        return "".join(translated_chunks)

if __name__ == "__main__":
    import os
    translator = Translator()
    sample_text = "Bonjour, comment ça va?"
    print("Translated text:")
    translated_text = translator.translate_text(sample_text, target_language='en')
    print(translated_text)
    detected_language = translator.detect_language(sample_text)
    print(f"Detected language: {detected_language}")
