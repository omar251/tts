import unittest
import asyncio
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import TTSApplication
from settings import AppSettings


class TestTTSApplicationIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.app = TTSApplication()

        # Create temporary input file
        self.input_file = os.path.join(self.temp_dir, 'test_input.txt')
        with open(self.input_file, 'w', encoding='utf-8') as f:
            f.write('This is a test sentence. How are you today?')

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('main.TTSGenerator')
    @patch('main.AudioPlayer')
    @patch('main.FileManager')
    def test_run_with_file_input_no_translation(self, mock_file_manager, mock_audio_player, mock_tts_generator):
        """Test running the application with file input and no translation."""
        # Mock the TTS generator
        mock_tts_instance = Mock()
        mock_tts_instance.generate_tts = AsyncMock(return_value=('test_audio.wav', 'test_text.txt'))
        mock_tts_generator.return_value = mock_tts_instance

        # Mock the audio player
        mock_audio_instance = Mock()
        mock_audio_instance.play_audio = Mock()
        mock_audio_player.return_value = mock_audio_instance

        # Mock the file manager
        mock_file_instance = Mock()
        mock_file_instance.create_output_directory = Mock()
        mock_file_instance.cleanup_temp_files = Mock()
        mock_file_manager.return_value = mock_file_instance

        # Run the application
        async def run_test():
            await self.app.run(input_text=self.input_file, is_file=True, target_language=None)

        # Execute the async test
        asyncio.run(run_test())

        # Verify that TTS was called
        mock_tts_instance.generate_tts.assert_called()

        # Verify that audio was played
        mock_audio_instance.play_audio.assert_called()

        # Verify file operations
        mock_file_instance.create_output_directory.assert_called()
        mock_file_instance.cleanup_temp_files.assert_called()

    @patch('main.TTSGenerator')
    @patch('main.AudioPlayer')
    @patch('main.FileManager')
    @patch('main.Translator')
    def test_run_with_text_input_and_translation(self, mock_translator, mock_file_manager, mock_audio_player, mock_tts_generator):
        """Test running the application with direct text input and translation."""
        # Mock the translator
        mock_translator_instance = Mock()
        mock_translator_instance.translate_text = Mock(return_value='This is translated text.')
        mock_translator.return_value = mock_translator_instance

        # Mock the TTS generator
        mock_tts_instance = Mock()
        mock_tts_instance.generate_tts = AsyncMock(return_value=('test_audio.wav', 'test_text.txt'))
        mock_tts_generator.return_value = mock_tts_instance

        # Mock the audio player
        mock_audio_instance = Mock()
        mock_audio_instance.play_audio = Mock()
        mock_audio_player.return_value = mock_audio_instance

        # Mock the file manager
        mock_file_instance = Mock()
        mock_file_instance.create_output_directory = Mock()
        mock_file_instance.cleanup_temp_files = Mock()
        mock_file_manager.return_value = mock_file_instance

        # Run the application
        async def run_test():
            await self.app.run(input_text="Bonjour le monde", is_file=False, target_language="en")

        # Execute the async test
        asyncio.run(run_test())

        # Verify that translation was called
        mock_translator_instance.translate_text.assert_called_with("Bonjour le monde", target_language="en")

        # Verify that TTS was called
        mock_tts_instance.generate_tts.assert_called()

        # Verify that audio was played
        mock_audio_instance.play_audio.assert_called()

    @patch('main.TTSGenerator')
    @patch('main.AudioPlayer')
    @patch('main.FileManager')
    def test_run_with_missing_file_fallback(self, mock_file_manager, mock_audio_player, mock_tts_generator):
        """Test that the application handles missing files gracefully."""
        # Mock the TTS generator
        mock_tts_instance = Mock()
        mock_tts_instance.generate_tts = AsyncMock(return_value=('test_audio.wav', 'test_text.txt'))
        mock_tts_generator.return_value = mock_tts_instance

        # Mock the audio player
        mock_audio_instance = Mock()
        mock_audio_instance.play_audio = Mock()
        mock_audio_player.return_value = mock_audio_instance

        # Mock the file manager
        mock_file_instance = Mock()
        mock_file_instance.create_output_directory = Mock()
        mock_file_instance.cleanup_temp_files = Mock()
        mock_file_manager.return_value = mock_file_instance

        # Run the application with non-existent file
        async def run_test():
            await self.app.run(input_text="nonexistent_file.txt", is_file=True, target_language=None)

        # Execute the async test
        asyncio.run(run_test())

        # Verify that TTS was called with fallback text
        mock_tts_instance.generate_tts.assert_called()

        # Get the call arguments to verify fallback text was used
        call_args = mock_tts_instance.generate_tts.call_args
        self.assertIn("I have no idea what to say", call_args[0][0])

    def test_text_chunking_integration(self):
        """Test that text chunking works correctly in the application."""
        # Test with a longer text that should be chunked
        long_text = "This is sentence one. This is sentence two! This is sentence three? This is sentence four."

        chunks = self.app.text_processor.split_text_into_chunks(long_text)

        # Verify that chunking occurred
        self.assertEqual(len(chunks), 4)
        self.assertEqual(chunks[0], "This is sentence one.")
        self.assertEqual(chunks[1], "This is sentence two!")
        self.assertEqual(chunks[2], "This is sentence three?")
        self.assertEqual(chunks[3], "This is sentence four.")

    @patch('main.asyncio.Queue')
    @patch('main.TTSGenerator')
    @patch('main.AudioPlayer')
    def test_concurrent_processing_and_playback(self, mock_audio_player, mock_tts_generator, mock_queue):
        """Test that concurrent processing and playback works correctly."""
        # Mock the queue
        mock_queue_instance = Mock()
        mock_queue_instance.put = AsyncMock()
        mock_queue_instance.get = AsyncMock()
        mock_queue_instance.task_done = Mock()
        mock_queue.return_value = mock_queue_instance

        # Mock the TTS generator
        mock_tts_instance = Mock()
        mock_tts_instance.generate_tts = AsyncMock(return_value=('test_audio.wav', 'test_text.txt'))
        mock_tts_generator.return_value = mock_tts_instance

        # Mock the audio player
        mock_audio_instance = Mock()
        mock_audio_instance.play_audio = Mock()
        mock_audio_player.return_value = mock_audio_instance

        # Test the talk method
        async def run_test():
            await self.app.talk("This is a test sentence. Another sentence!", "test_output")

        # Execute the async test
        asyncio.run(run_test())

        # Verify that TTS generation was called for each chunk
        self.assertGreaterEqual(mock_tts_instance.generate_tts.call_count, 1)

        # Verify that items were put in the queue
        self.assertGreaterEqual(mock_queue_instance.put.call_count, 1)


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Create a test input file
        self.test_input_file = os.path.join(self.temp_dir, 'test_input.txt')
        with open(self.test_input_file, 'w', encoding='utf-8') as f:
            f.write('Hello world. This is a test.')

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('main.TTSApplication')
    @patch('sys.argv', ['tts', '-t', 'Hello world'])
    def test_cli_text_input(self, mock_tts_app):
        """Test CLI with text input."""
        # Mock the TTS application
        mock_app_instance = Mock()
        mock_app_instance.run = AsyncMock()
        mock_tts_app.return_value = mock_app_instance

        # Import and run main (this will use the mocked sys.argv)
        from main import main
        main()

        # Verify that the app was called with correct parameters
        mock_app_instance.run.assert_called_once()
        call_args = mock_app_instance.run.call_args
        self.assertEqual(call_args[0][0], 'Hello world')  # input_text
        self.assertFalse(call_args[1]['is_file'])  # is_file
        self.assertIsNone(call_args[1]['target_language'])  # target_language

    @patch('main.TTSApplication')
    @patch('sys.argv', ['tts', '-f', 'test_file.txt', '-l', 'en'])
    def test_cli_file_input_with_translation(self, mock_tts_app):
        """Test CLI with file input and translation."""
        # Mock the TTS application
        mock_app_instance = Mock()
        mock_app_instance.run = AsyncMock()
        mock_tts_app.return_value = mock_app_instance

        # Import and run main
        from main import main
        main()

        # Verify that the app was called with correct parameters
        mock_app_instance.run.assert_called_once()
        call_args = mock_app_instance.run.call_args
        self.assertEqual(call_args[0][0], 'test_file.txt')  # input_text
        self.assertTrue(call_args[1]['is_file'])  # is_file
        self.assertEqual(call_args[1]['target_language'], 'en')  # target_language


if __name__ == '__main__':
    unittest.main(verbosity=2)
