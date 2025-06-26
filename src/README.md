# Source Code

This directory contains the source code for the TTS system.

## Main Components

- `main.py`: CLI entry point and application orchestration
- `tts_service.py`: Unified service layer for CLI and web interfaces
- `web_server.py`: Web interface and API endpoints
- `tts_generator.py`: TTS generation using Microsoft Edge TTS
- `translator.py`: Translation using Google Translate
- `audio_player.py`: Audio playback with synchronized text display
- `text_processor.py`: Text processing and chunking
- `file_manager.py`: Unified file management system
- `settings.py`: Configuration settings
- `logging_utils.py`: Logging utilities

## Architecture

The system is designed with a modular architecture that separates concerns:

1. **Interface Layer**: `main.py` (CLI) and `web_server.py` (Web)
2. **Service Layer**: `tts_service.py` bridges CLI and web functionality
3. **Core Components**: Translation, TTS generation, audio playback, text processing
4. **Infrastructure**: File management, settings, logging

This design allows for easy extension and maintenance of the system.