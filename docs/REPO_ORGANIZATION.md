# Repository Organization

This document describes the organization of the repository after the restructuring.

## Directory Structure

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

## Changes Made

1. **Documentation Organization**
   - Moved all documentation files to the `docs/` directory
   - Created an index file for the documentation
   - Updated links in documentation to reflect the new structure

2. **Test Organization**
   - Moved all test files to the `tests/` directory
   - Updated test files to work with the new directory structure
   - Added a README for the tests directory

3. **Example Organization**
   - Moved example data files to `examples/data/` directory
   - Added a README for the examples directory

4. **Script Organization**
   - Moved utility scripts to the `scripts/` directory
   - Added a README for the scripts directory

5. **Source Code Organization**
   - Added a README for the source code directory
   - Kept the source code in the `src/` directory

6. **Static Files Organization**
   - Added a README for the static files directory
   - Kept the static files in the `static/` directory

7. **Temporary Files Organization**
   - Added a `.gitkeep` file to ensure the `temp/` directory exists in the repository
   - Updated the `.gitignore` file to ignore temporary files

8. **Configuration Updates**
   - Updated the `config.yaml` file to reflect the new directory structure
   - Updated the `docker-compose.yml` file to reflect the new directory structure
   - Updated the `Makefile` to work with the new directory structure

9. **README Updates**
   - Updated the main README.md file to reflect the new directory structure
   - Added README files to each directory to explain its purpose

## Benefits

1. **Better Organization**: Files are logically grouped by purpose
2. **Improved Documentation**: Each directory has its own README
3. **Easier Navigation**: Clear separation of concerns
4. **Better Maintainability**: Easier to find and update files
5. **Cleaner Repository**: Temporary files are properly ignored

## Future Improvements

1. **Add More Tests**: Add more comprehensive tests for all components
2. **Improve Documentation**: Add more detailed documentation for each component
3. **Add CI/CD**: Add GitHub Actions or other CI/CD pipeline
4. **Add Code Coverage**: Add code coverage reporting
5. **Add API Documentation**: Add detailed API documentation for web interface