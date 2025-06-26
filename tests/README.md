# Tests

This directory contains test files for the TTS system.

## Available Tests

- `test_unified_file_management.py`: Tests for the unified file management system
- `test_unified_system.py`: Tests for the unified TTS system (CLI and web components)
- `test_server_option.py`: Tests for the CLI --server option functionality

## Running Tests

You can run the tests using the Makefile commands:

```bash
# Run all tests
make test

# Run file management tests
make test-file-management

# Run server option tests
make test-server-option

# Run with coverage
make test-cov
```