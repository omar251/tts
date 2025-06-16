# Text-to-Speech CLI Tool Documentation

## Overview

This Python CLI tool provides a flexible text-to-speech (TTS) solution that can process input from a file or direct text input. It translates the input to English if necessary, converts it to speech using the Microsoft Edge TTS engine, and plays the audio while displaying synchronized text output. The script processes the text in chunks, allowing for smoother playback of long texts.

## Features

- Accepts input from a file or direct text input via command-line arguments
- Translates input text to English (if needed) using Google Translate
- Converts text to speech using Microsoft Edge TTS
- Plays audio with synchronized text display
- Processes text in chunks for better handling of long texts
- Supports various voices and languages (configurable)
- Modular design for easy maintenance and extensibility

## Requirements

- Python 3.7+
- pygame
- edge-tts
- deep-translator

## Installation

1. Ensure you have Python 3.7 or later installed on your system.
2. Install the required packages:

```bash
pip install pygame edge-tts deep-translator
```

3. Clone or download the project to your local machine.

## Project Structure

```
tts/
├── src/                  # Main source code
│   ├── audio_player.py   # Audio playback management
│   ├── config.py         # Configuration settings
│   ├── file_manager.py   # File operations
│   ├── main.py           # Entry point
│   ├── text_processor.py # Text processing
│   ├── translator.py     # Translation functionality
│   └── tts_generator.py  # TTS generation
├── examples/             # Sample files
│   ├── input.txt         # Example input file
│   └── translated.txt    # Example translated output
├── output_files/         # Generated audio files
├── pyproject.toml        # Python project configuration
└── README.md             # Documentation
```

## Usage

The tool can be used in three ways:

1. Default mode (using `INPUT_FILE` from config):
```bash
python -m src.main
```

2. Process a specific file:
```bash
python -m src.main -f examples/input.txt
```

3. Process direct text input:
```bash
python -m src.main -t "Hello, how are you?"
```

## Configuration

You can modify the following constants in the `src/config.py` file to customize the tool's behavior:

- `INPUT_FILE`: Default input text file path (relative to project root)
- `TRANSLATED_FILE`: Path for the translated text file (relative to project root)
- `OUTPUT_DIRECTORY`: Directory to store generated audio files
- `SPECIAL_CHARACTERS`: Characters used to split the text into chunks
- `DELIMITER`: Delimiter used in word boundary files

## Main Components

### `TTSApplication` class

The main application class that orchestrates the entire TTS process.

### `Translator` class

Handles text translation using Google Translate.

### `TTSGenerator` class

Generates TTS audio using the Microsoft Edge TTS engine.

### `AudioPlayer` class

Manages audio playback and synchronized text display.

### `TextProcessor` class

Processes and splits text into chunks.

### `FileManager` class

Handles file operations and cleanup.

## Error Handling

The tool includes error handling for common issues such as missing input files or TTS generation errors. Error messages will be displayed in the console if any issues occur during execution.

## Limitations

- Audio playback relies on the pygame library, which may have platform-specific limitations.
- Translation quality depends on the Google Translate service.
- Must be run as a module from the project root directory (`python -m src.main`).

## Contributing

Feel free to fork this project, submit issues, or provide pull requests to improve the tool.

## License

[Specify the license under which this tool is released, e.g., MIT, GPL, etc.]