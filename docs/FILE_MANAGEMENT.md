# Unified File Management System

## Overview

The TTS system now uses a unified file management system that organizes all artifacts and outputs in a structured, session-based directory hierarchy. This approach improves organization, simplifies cleanup, and makes debugging easier.

## Directory Structure

```
temp/
├── session_YYYYMMDD_HHMMSS_uuid/  # Session-specific directory
│   ├── audio/                     # Audio files (.wav)
│   ├── text/                      # Text files with word boundaries (.txt)
│   ├── translation/               # Translation files
│   └── cache/                     # Cache files (voices, etc.)
└── session_*/                     # Other sessions...
```

## Key Features

### 1. Session-Based Organization

- Each TTS run creates a unique session with its own directory
- Sessions are automatically named with timestamp and UUID
- All files related to a session are grouped together

### 2. File Type Categorization

- **Audio files**: Stored in `audio/` subdirectory
- **Text files**: Stored in `text/` subdirectory with word boundaries
- **Translation files**: Stored in `translation/` subdirectory
- **Cache files**: Stored in `cache/` subdirectory

### 3. Automatic Cleanup

- Session files are automatically cleaned up after processing
- Old sessions are automatically removed after a configurable time period
- Cache files can be preserved while cleaning up other files

### 4. Consistent Naming

- All files follow a consistent naming convention
- File names include timestamps and identifiers
- Chunk files are numbered sequentially

## Usage

### In Code

The unified file manager is used throughout the codebase:

```python
# Initialize the file manager
from file_manager import UnifiedFileManager
file_manager = UnifiedFileManager("temp")

# Create audio file paths
audio_file, text_file = file_manager.create_audio_file_path("prefix", chunk_id=0)

# Create translation file path
translation_file = file_manager.create_translation_file_path("en", "fr")

# Create cache file path
cache_file = file_manager.create_cache_file_path("voices", ".json")

# Get web URL for audio file
audio_url = file_manager.get_web_audio_url(audio_file)

# Clean up session files
file_manager.cleanup_session_files()

# Clean up old sessions
file_manager.cleanup_old_sessions(max_age_hours=24)
```

### Command Line

Use the Makefile to test and manage the file system:

```bash
# Test the unified file management system
make test-file-management

# Clean up all output files
make clean-output
```

## Benefits

1. **Better Organization**: Files are logically grouped by session and type
2. **Improved Debugging**: Easy to trace files related to a specific TTS run
3. **Automatic Cleanup**: No manual cleanup required
4. **Disk Space Management**: Old files are automatically removed
5. **Web Compatibility**: Consistent URL generation for web interface
6. **Session Tracking**: Metadata about each session is maintained

## Implementation Details

The unified file management system is implemented in `src/file_manager.py` with the `UnifiedFileManager` class. It provides a comprehensive API for file operations while maintaining backward compatibility with the existing `FileManager` class.

### Singleton Pattern

The `UnifiedFileManager` implements a singleton pattern to ensure that only one instance exists across the entire application. This prevents the creation of multiple session directories for what should be a single logical session.

```python
# The singleton instance is automatically shared across all components
file_manager1 = UnifiedFileManager()
file_manager2 = UnifiedFileManager()

# Both variables reference the same instance with the same session
assert file_manager1 is file_manager2
assert file_manager1.session_id == file_manager2.session_id
```

This ensures that all components (CLI, web server, TTS service) use the same session directory.

### Key Methods

- `create_audio_file_path()`: Create paths for audio and text files
- `create_translation_file_path()`: Create path for translation files
- `create_cache_file_path()`: Create path for cache files
- `get_web_audio_url()`: Generate web-accessible URL for audio files
- `cleanup_session_files()`: Clean up files from the current session
- `cleanup_old_sessions()`: Clean up old session directories
- `get_session_info()`: Get information about the current session
- `get_disk_usage()`: Get disk usage information

## Configuration

The base directory for all temporary files is configured in `config.yaml`:

```yaml
# Directory to store generated audio files (relative to project root)
# Note: With unified file management, all artifacts are organized in
# session-based subdirectories: temp/session_*/audio/, temp/session_*/text/, etc.
output_directory: temp
```

This can be overridden with the `TTS_OUTPUT_DIRECTORY` environment variable.