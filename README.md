# Text-to-Speech CLI and Web Application

## Overview

This project provides a flexible text-to-speech (TTS) solution that can process input from a file or direct text input, with both CLI and web interfaces. It translates the input to the target language if requested, converts it to speech using the Microsoft Edge TTS engine, and plays the audio while displaying synchronized text output. The system processes the text in chunks, allowing for smoother playback of long texts.

## Features

- **Multiple Interfaces**: CLI and web-based interfaces for flexibility
- **Input Options**: Accepts input from a file or direct text input
- **Translation Support**: Optional translation to target language using Google Translate
- **High-Quality TTS**: Uses Microsoft Edge TTS for natural-sounding speech
- **Streaming Playback**: Processes text in chunks for smoother playback
- **Session Management**: Unified file management with session-based organization
- **Docker Support**: Easy deployment with Docker and docker-compose

## Requirements

- Python 3.12+
- See dependencies in `pyproject.toml`

## Installation

1. Ensure you have Python 3.12 or later installed on your system.
2. Clone or download the project to your local machine.
3. From the project root, install the package and dependencies:

```bash
pip install .
```

This will install all required dependencies and make the `tts` CLI available globally.

## Project Structure

```
tts/
├── docs/                  # Documentation
│   ├── QUICK_START.md     # Quick start guide
│   ├── FILE_MANAGEMENT.md # File management documentation
│   └── ...                # Other documentation
├── src/                   # Source code
│   ├── audio_player.py    # Audio playback management
│   ├── file_manager.py    # Unified file management system
│   ├── main.py            # CLI entry point
│   ├── text_processor.py  # Text processing
│   ├── translator.py      # Translation functionality
│   ├── tts_generator.py   # TTS generation
│   ├── tts_service.py     # Unified TTS service layer
│   └── web_server.py      # Web interface
├── tests/                 # Test files
│   ├── test_unified_file_management.py
│   └── test_unified_system.py
├── examples/              # Example files
│   └── data/              # Sample data files
├── scripts/               # Utility scripts
│   └── convert_pdfs_to_txt.py
├── static/                # Static web files
├── temp/                  # Generated audio and text files
│   └── session_*/         # Session-based directories for artifacts
├── config.yaml            # Configuration file
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── pyproject.toml         # Python project configuration
└── Makefile               # Build automation
```

## Usage

### CLI Interface

After installation, you can use the CLI from anywhere:

1. Default mode (uses `input_file` from config):

```bash
tts
```

2. Process a specific file:

```bash
tts -f examples/data/input.txt
```

3. Process direct text input:

```bash
tts -t "Hello, how are you?"
```

#### Optional: Translate to a target language

By default, the tool uses the original text with no translation.  
To translate to a specific language, use the `--language` (or `-l`) flag with the target language code (e.g., `en` for English, `fr` for French):

```bash
tts -t "Bonjour tout le monde" --language en
tts -f examples/data/input.txt --language fr
```

If `--language` is not provided, the original text is used without translation.

### Web Interface

Start the web server:

```bash
# Start the web server
python -m src.web_server

# Or use make
make run-web

# Access the web interface at http://localhost:8000
```

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up -d
```

## Configuration

You can customize the tool's behavior by editing the `config.yaml` file in the project root:

- `input_file`: Default input text file path (relative to project root)
- `translated_file`: Path for the translated text file (relative to project root)
- `output_directory`: Directory to store generated audio files
- `special_characters`: Characters used to split the text into chunks
- `delimiter`: Delimiter used in word boundary files
- `tts_voice`: Default TTS voice (see `edge-tts --list-voices` for options)

You can also override any setting using environment variables (e.g., `TTS_INPUT_FILE`, `TTS_OUTPUT_DIRECTORY`).

### File Management

The system uses a unified file management approach that organizes all artifacts in session-based directories:

```
temp/
├── session_YYYYMMDD_HHMMSS_uuid/  # Session-specific directory
│   ├── audio/                     # Audio files (.wav)
│   ├── text/                      # Text files with word boundaries (.txt)
│   ├── translation/               # Translation files
│   └── cache/                     # Cache files (voices, etc.)
└── session_*/                     # Other sessions...
```

For more details, see [docs/FILE_MANAGEMENT.md](docs/FILE_MANAGEMENT.md).

## Main Components

### `TTSApplication` class

The main application class that orchestrates the entire TTS process.

### `TTSService` class

Unified service layer that bridges CLI and web functionality.

### `Translator` class

Handles text translation using Google Translate.

### `TTSGenerator` class

Generates TTS audio using the Microsoft Edge TTS engine.

### `AudioPlayer` class

Manages audio playback and synchronized text display.

### `TextProcessor` class

Processes and splits text into chunks.

### `UnifiedFileManager` class

Handles file operations, organization, and cleanup with session-based management.

## Development

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Clean up temporary files
make clean-output
```

## Documentation

- [Quick Start Guide](docs/QUICK_START.md): Get started quickly with the TTS system
- [File Management](docs/FILE_MANAGEMENT.md): Learn about the unified file management system
- [Component Comparison](docs/COMPONENT_COMPARISON.md): Understand the different components

## Error Handling

The tool includes error handling for common issues such as missing input files or TTS generation errors. Error messages will be displayed in the console if any issues occur during execution.

## Limitations

- Audio playback relies on the pygame library, which may have platform-specific limitations.
- Translation quality depends on the Google Translate service.

## Contributing

Feel free to fork this project, submit issues, or provide pull requests to improve the tool.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.