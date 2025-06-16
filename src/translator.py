# translator.py
from deep_translator import GoogleTranslator

class Translator:
    def translate_file(self, input_file: str, output_file: str) -> None:
        translated = GoogleTranslator(source='auto', target='en').translate_file(input_file)
        with open(output_file, "w", encoding='utf-8') as f:
            f.write(translated)

    def translate_text(self, text: str) -> str:
        return GoogleTranslator(source='auto', target='en').translate(text)

if __name__ == "__main__":
    import os

    # Demo usage
    translator = Translator()

    # File translation
    input_file = "sample_input.txt"
    output_file = "sample_translated.txt"

    with open(input_file, "w", encoding='utf-8') as f:
        f.write("Bonjour le monde!")

    translator.translate_file(input_file, output_file)

    print(f"Translated content saved to {output_file}")

    with open(output_file, "r", encoding='utf-8') as f:
        print(f"Translated text from file: {f.read()}")

    # Direct text translation
    input_text = "Hola, ¿cómo estás?"
    translated_text = translator.translate_text(input_text)
    print(f"Translated text directly: {translated_text}")

    # Clean up
    os.remove(input_file)
    os.remove(output_file)
