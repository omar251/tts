# translator.py
from googletrans import Translator as GoogleTranslator

MAX_TRANSLATE_CHARS = 5000

from .logging_utils import VERBOSE, vprint

class Translator:
    def __init__(self):
        self.translator = GoogleTranslator()

    def translate_file(self, input_file: str, output_file: str) -> None:
        vprint(f"[Translator] Reading input file: {input_file}")
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
        vprint("[Translator] Translating file content...")
        translated = self.translate_text(text)
        vprint(f"[Translator] Writing translated content to: {output_file}")
        with open(output_file, "w", encoding='utf-8') as f:
            f.write(translated)

    def translate_text(self, text: str) -> str:
        vprint("[Translator] Splitting text into chunks...")
        # Split text into <=5000 char chunks for translation
        chunks = []
        current = ""
        for line in text.splitlines(keepends=True):
            if len(current) + len(line) > MAX_TRANSLATE_CHARS:
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
            translated_chunks.append(self.translator.translate(chunk, src='auto', dest='en').text)
        vprint("[Translator] All chunks translated.")
        return "".join(translated_chunks)

if __name__ == "__main__":
    import os
