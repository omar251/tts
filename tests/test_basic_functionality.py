import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from text_processor import TextProcessor
from translator import Translator
from settings import AppSettings


class TestTextProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = TextProcessor()

    def test_split_text_into_chunks_basic(self):
        """Test basic text splitting functionality."""
        text = "Hello world. How are you? I'm fine!"
        chunks = self.processor.split_text_into_chunks(text)

        expected = ["Hello world.", "How are you?", "I'm fine!"]
        self.assertEqual(chunks, expected)

    def test_split_text_with_semicolon(self):
        """Test text splitting with semicolons."""
        text = "First part; second part; third part."
        chunks = self.processor.split_text_into_chunks(text)

        expected = ["First part;", "second part;", "third part."]
        self.assertEqual(chunks, expected)

    def test_split_text_with_newlines(self):
        """Test text splitting with newline characters."""
        text = "Line one\nLine two\nLine three"
        chunks = self.processor.split_text_into_chunks(text)

        expected = ["Line one", "Line two", "Line three"]
        self.assertEqual(chunks, expected)

    def test_empty_text(self):
        """Test splitting empty text."""
        text = ""
        chunks = self.processor.split_text_into_chunks(text)

        self.assertEqual(chunks, [])

    def test_text_without_special_characters(self):
        """Test text that doesn't contain any splitting characters."""
        text = "This is a continuous text without punctuation"
        chunks = self.processor.split_text_into_chunks(text)

        self.assertEqual(chunks, ["This is a continuous text without punctuation"])


class TestTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = Translator()

    @patch('translator.GoogleTranslator')
    def test_translate_text_with_target_language(self, mock_google_translator):
        """Test translation when target language is specified."""
        # Mock the Google Translator
        mock_translator_instance = Mock()
        mock_translator_instance.translate.return_value.text = "Hello world"
        mock_google_translator.return_value = mock_translator_instance

        # Create new translator instance to use mocked GoogleTranslator
        translator = Translator()

        result = translator.translate_text("Bonjour le monde", target_language="en")

        self.assertEqual(result, "Hello world")
        mock_translator_instance.translate.assert_called_once()

    def test_translate_text_without_target_language(self):
        """Test translation when no target language is specified."""
        original_text = "Hello world"
        result = self.translator.translate_text(original_text, target_language=None)

        self.assertEqual(result, original_text)

    def test_translate_text_empty_target_language(self):
        """Test translation when target language is empty string."""
        original_text = "Hello world"
        result = self.translator.translate_text(original_text, target_language="")

        self.assertEqual(result, original_text)

    @patch('translator.GoogleTranslator')
    def test_detect_language(self, mock_google_translator):
        """Test language detection functionality."""
        # Mock the Google Translator
        mock_translator_instance = Mock()
        mock_detection = Mock()
        mock_detection.lang = "fr"
        mock_translator_instance.detect.return_value = mock_detection
        mock_google_translator.return_value = mock_translator_instance

        # Create new translator instance to use mocked GoogleTranslator
        translator = Translator()

        result = translator.detect_language("Bonjour le monde")

        self.assertEqual(result, "fr")
        mock_translator_instance.detect.assert_called_once_with("Bonjour le monde")

    @patch('translator.GoogleTranslator')
    def test_translate_long_text_chunking(self, mock_google_translator):
        """Test that long text is properly chunked for translation."""
        # Mock the Google Translator
        mock_translator_instance = Mock()
        mock_translator_instance.translate.return_value.text = "Translated chunk"
        mock_google_translator.return_value = mock_translator_instance

        # Create new translator instance to use mocked GoogleTranslator
        translator = Translator()

        # Create a long text that would exceed the chunk limit
        long_text = "This is a test sentence. " * 500  # Should exceed 5000 chars

        result = translator.translate_text(long_text, target_language="fr")

        # Should have called translate multiple times due to chunking
        self.assertGreater(mock_translator_instance.translate.call_count, 1)
        self.assertIn("Translated chunk", result)


class TestAppSettings(unittest.TestCase):
    def test_default_settings(self):
        """Test that default settings are properly initialized."""
        # Create a temporary settings instance without loading external config
        settings = AppSettings()

        # Test default values
        self.assertEqual(settings.input_file, 'examples/input.txt')
        self.assertEqual(settings.translated_file, 'output_files/translated.txt')
        self.assertEqual(settings.output_directory, 'output_files')
        self.assertIn('.', settings.special_characters)
        self.assertIn('?', settings.special_characters)
        self.assertIn('!', settings.special_characters)
        self.assertEqual(settings.delimiter, '***WORD_BOUNDARY***')
        self.assertEqual(settings.max_translate_chars, 5000)

    @patch.dict(os.environ, {
        'TTS_INPUT_FILE': 'test_input.txt',
        'TTS_OUTPUT_DIRECTORY': 'test_output',
        'TTS_VOICE': 'en-GB-SoniaNeural',
        'TTS_MAX_TRANSLATE_CHARS': '3000'
    })
    def test_environment_variable_override(self):
        """Test that environment variables properly override default settings."""
        settings = AppSettings()

        self.assertEqual(settings.input_file, 'test_input.txt')
        self.assertEqual(settings.output_directory, 'test_output')
        self.assertEqual(settings.tts_voice, 'en-GB-SoniaNeural')
        self.assertEqual(settings.max_translate_chars, 3000)


if __name__ == '__main__':
    # Set up test environment
    unittest.main(verbosity=2)
