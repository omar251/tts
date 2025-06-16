# text_processor.py
from typing import List
from . import config

class TextProcessor:
    def split_text_into_chunks(self, text: str) -> List[str]:
        chunks = []
        current_chunk = ""
        for char in text:
            current_chunk += char
            if char in config.SPECIAL_CHARACTERS:
                chunks.append(current_chunk.strip())
                current_chunk = ""
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

if __name__ == "__main__":
    processor = TextProcessor()
    sample_text = "Hello, world! This is a test. How are you? I'm fine; thanks for asking."
    chunks = processor.split_text_into_chunks(sample_text)

    print("Text split into chunks:")
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}: {chunk}")
