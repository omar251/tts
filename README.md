# Text-to-Speech CLI Tool Documentation

## Overview

This Python CLI tool provides a flexible text-to-speech (TTS) solution that can process input from a file or direct text input. It translates the input to English if necessary, converts it to speech using the Microsoft Edge TTS engine, and plays the audio while displaying synchronized text output. The script processes the text in chunks, allowing for smoother playback of long texts.

## Features

- Accepts input from a file or direct text input via command-line arguments
- Optionally translates input text to a target language using Google Translate (only if `--language` flag is set)
- Converts text to speech using Microsoft Edge TTS
- Plays audio with synchronized text display
- Processes text in chunks for better handling of long texts
- Supports various voices and languages (configurable)
- Modular design for easy maintenance and extensibility

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

After installation, you can use the CLI from anywhere:

1. Default mode (uses `input_file` from config):

```bash
tts
```

2. Process a specific file:

```bash
tts -f examples/input.txt
```

3. Process direct text input:

```bash
tts -t "Hello, how are you?"
```

### Optional: Translate to a target language

By default, the tool uses the original text with no translation.  
To translate to a specific language, use the `--language` (or `-l`) flag with the target language code (e.g., `en` for English, `fr` for French):

```bash
tts -t "Bonjour tout le monde" --language en
tts -f examples/input.txt --language fr
```

If `--language` is not provided, the original text is used without translation.

## Configuration

You can customize the tool's behavior by editing the `config.yaml` file in the project root:

- `input_file`: Default input text file path (relative to project root)
- `translated_file`: Path for the translated text file (relative to project root)
- `output_directory`: Directory to store generated audio files
- `special_characters`: Characters used to split the text into chunks
- `delimiter`: Delimiter used in word boundary files
- `tts_voice`: Default TTS voice (see `edge-tts --list-voices` for options)

You can also override any setting using environment variables (e.g., `TTS_INPUT_FILE`, `TTS_OUTPUT_DIRECTORY`).

## Main Components

### `TTSApplication` class

The main application class that orchestrates the entire TTS process.

### `Translator` class

Handles text translation using Google Translate.  
Translation is only performed if a target language is specified via the `--language` flag.

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

## Contributing

Feel free to fork this project, submit issues, or provide pull requests to improve the tool.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.