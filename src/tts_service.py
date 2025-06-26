#!/usr/bin/env python3
"""
Unified TTS Service Layer

This module provides a unified interface for TTS functionality that can be used by both
the CLI application and the web interface. It bridges the existing CLI streaming logic
with the web-based streaming requirements.
"""

import asyncio
import os
import tempfile
import time
from datetime import datetime
from typing import Optional, List, Tuple, AsyncGenerator
import logging

from .main import TTSApplication
from .file_manager import UnifiedFileManager
from .settings import settings

logger = logging.getLogger(__name__)

class TTSService:
    """
    Unified TTS service that provides both CLI and web streaming capabilities.
    
    This service acts as a bridge between the existing CLI streaming logic
    and the web-based streaming requirements, ensuring both use the same
    high-quality TTS processing while supporting different output methods.
    """
    
    def __init__(self):
        """Initialize the TTS service with CLI components."""
        self.tts_app = TTSApplication()
        self.unified_file_manager = UnifiedFileManager(settings.output_directory)
        self._setup_directories()
    
    def _setup_directories(self):
        """Ensure required directories exist."""
        os.makedirs(settings.output_directory, exist_ok=True)
    
    async def stream_tts_cli(self, text: str, output_file: str, target_language: Optional[str] = None) -> None:
        """
        Stream TTS using the existing CLI logic.
        
        This method preserves the original CLI streaming behavior where audio
        is played locally through the audio player.
        
        Args:
            text: Text to convert to speech
            output_file: Base output file path
            target_language: Optional target language for translation
        """
        logger.info(f"Starting CLI TTS streaming for text: {text[:50]}...")
        
        # Use existing CLI logic with translation support
        if target_language:
            translated_text = self.tts_app.translator.translate_text(text, target_language)
        else:
            translated_text = text
        
        # Use the existing streaming talk method
        await self.tts_app.talk(translated_text, output_file)
        
        logger.info("CLI TTS streaming completed")
    
    async def stream_tts_web(self, text: str, voice: Optional[str] = None, 
                           target_language: Optional[str] = None) -> AsyncGenerator[Tuple[str, str, str], None]:
        """
        Stream TTS for web interface using CLI components.
        
        This method uses the same text processing and TTS generation logic as the CLI
        but yields results suitable for web streaming instead of local playback.
        
        Args:
            text: Text to convert to speech
            voice: Optional specific voice to use
            target_language: Optional target language for translation
            
        Yields:
            Tuple of (audio_file_path, audio_url, paragraph_text)
        """
        logger.info(f"Starting web TTS streaming for text: {text[:50]}...")
        
        try:
            # Step 1: Translation (if requested)
            if target_language:
                logger.info(f"Translating text to {target_language}")
                processed_text = self.tts_app.translator.translate_text(text, target_language)
            else:
                processed_text = text
            
            # Step 2: Use CLI text processing for chunking
            # Split by paragraphs (similar to webtts) but use CLI logic for consistency
            paragraphs = self._split_into_paragraphs(processed_text)
            logger.info(f"Split text into {len(paragraphs)} paragraphs")
            
            # Step 3: Process each paragraph using CLI TTS logic
            for i, paragraph in enumerate(paragraphs):
                logger.info(f"Processing paragraph {i+1}/{len(paragraphs)}")
                
                # Use unified file manager for consistent file paths
                audio_file, text_file = self.unified_file_manager.create_audio_file_path("web_output", i)
                
                # Use existing TTS generator with voice override if specified
                if voice:
                    # Temporarily override the voice setting
                    original_voice = getattr(settings, 'tts_voice', None)
                    settings.tts_voice = voice
                
                try:
                    # Use the same TTS generation logic as CLI
                    result_audio, result_text = await self.tts_app.tts_generator.generate_tts(
                        paragraph, audio_file, text_file
                    )
                    
                    if result_audio and os.path.exists(result_audio):
                        # Generate web-accessible URL using unified file manager
                        audio_url = self.unified_file_manager.get_web_audio_url(result_audio)
                        
                        logger.info(f"Generated audio for paragraph {i+1}: {audio_url}")
                        yield result_audio, audio_url, paragraph
                    else:
                        logger.error(f"Failed to generate audio for paragraph {i+1}")
                        
                finally:
                    # Restore original voice setting
                    if voice and 'original_voice' in locals():
                        settings.tts_voice = original_voice
        
        except Exception as e:
            logger.error(f"Error in web TTS streaming: {e}")
            raise
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs for web streaming.
        
        This method provides paragraph-based splitting similar to the webtts branch
        but can be enhanced to use the CLI text processor for more sophisticated chunking.
        
        Args:
            text: Text to split
            
        Returns:
            List of paragraph strings
        """
        # Basic paragraph splitting (similar to webtts)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        
        # If no paragraph breaks found, use CLI text processor for intelligent chunking
        if len(paragraphs) == 1 and len(text) > 200:
            logger.info("No paragraph breaks found, using CLI text processor for chunking")
            paragraphs = self.tts_app.text_processor.split_text_into_chunks(text)
        
        return paragraphs
    
    async def get_available_voices(self) -> List[dict]:
        """
        Get list of available TTS voices.
        
        This method provides voice information for the web interface,
        using the same voice management as the CLI.
        
        Returns:
            List of voice dictionaries
        """
        try:
            # Use the existing voice loading logic from TTS generator
            voices = await self.tts_app.tts_generator.load_voices_from_file()
            
            if not voices:
                # If no cached voices, fetch them
                from edge_tts import VoicesManager
                voices_manager = await VoicesManager.create()
                voices = voices_manager.voices
                
                # Cache them using existing logic
                await self.tts_app.tts_generator.save_voices_to_file(voices)
            
            return voices
        
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []
    
    async def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old audio files to prevent disk space issues.
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
            
        Returns:
            Number of files cleaned up
        """
        # Use unified file manager for cleanup
        cleanup_count = self.unified_file_manager.cleanup_old_sessions(max_age_hours)
        
        logger.info(f"Cleaned up {cleanup_count} old sessions")
        return cleanup_count
    
    async def health_check(self) -> dict:
        """
        Perform a health check of the TTS service.
        
        Returns:
            Dictionary with health status information
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        try:
            # Check TTS generator
            test_text = "Health check test"
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_text:
                    result = await self.tts_app.tts_generator.generate_tts(
                        test_text, temp_audio.name, temp_text.name
                    )
                    health_status["components"]["tts_generator"] = "healthy" if result[0] else "unhealthy"
                    
                    # Clean up test files
                    try:
                        os.unlink(temp_audio.name)
                        os.unlink(temp_text.name)
                    except:
                        pass
            
            # Check translator
            try:
                test_translation = self.tts_app.translator.translate_text("Hello", "fr")
                health_status["components"]["translator"] = "healthy" if test_translation else "unhealthy"
            except:
                health_status["components"]["translator"] = "unhealthy"
            
            # Check text processor
            try:
                chunks = self.tts_app.text_processor.split_text_into_chunks("Test text for chunking.")
                health_status["components"]["text_processor"] = "healthy" if chunks else "unhealthy"
            except:
                health_status["components"]["text_processor"] = "unhealthy"
            
            # Overall status
            unhealthy_components = [k for k, v in health_status["components"].items() if v == "unhealthy"]
            if unhealthy_components:
                health_status["status"] = "degraded"
                health_status["issues"] = unhealthy_components
        
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status

# Convenience functions for backward compatibility
async def quick_cli_tts(text: str, output_file: str, target_language: Optional[str] = None) -> None:
    """Quick function for CLI TTS using the service layer."""
    service = TTSService()
    await service.stream_tts_cli(text, output_file, target_language)

async def quick_web_tts(text: str, voice: Optional[str] = None, 
                       target_language: Optional[str] = None) -> AsyncGenerator[Tuple[str, str, str], None]:
    """Quick function for web TTS using the service layer."""
    service = TTSService()
    async for result in service.stream_tts_web(text, voice, target_language):
        yield result