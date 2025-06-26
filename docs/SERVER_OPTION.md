# CLI Server Option Documentation

## Overview

The `--server` option allows you to run the web server directly from the CLI tool, providing a unified entry point for both CLI and web functionality. This eliminates the need to remember separate commands for different modes.

## Usage

### Basic Server Mode

```bash
# Start the web server with default settings
python -m src.main --server

# Access the web interface at http://127.0.0.1:8000
```

### Server with Custom Configuration

```bash
# Custom host and port
python -m src.main --server --host 0.0.0.0 --port 8080

# Development mode with auto-reload
python -m src.main --server --reload

# Production mode with custom host
python -m src.main --server --host 0.0.0.0 --port 8000

# Verbose logging for debugging
python -m src.main --server --verbose --reload
```

## Arguments

### Server-Specific Arguments

- `--server`: Enable server mode (required for all other server options)
- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to bind to (default: 8000)
- `--reload`: Enable auto-reload for development (restarts server on code changes)

### Common Arguments

- `--verbose`: Enable verbose logging (works in both CLI and server modes)

## Validation Rules

1. **Server-only arguments**: `--host`, `--port`, and `--reload` can only be used with `--server`
2. **Mode exclusivity**: Cannot use `--file` or `--text` with `--server` mode
3. **Argument forwarding**: All valid arguments are properly forwarded to the web server

## Examples

### Development Workflow

```bash
# Start development server with auto-reload and verbose logging
python -m src.main --server --reload --verbose

# The server will restart automatically when you modify the code
```

### Production Deployment

```bash
# Start production server accessible from all interfaces
python -m src.main --server --host 0.0.0.0 --port 8000

# Or use the Makefile shortcut
make run-web-prod
```

### Testing Different Configurations

```bash
# Test on different port
python -m src.main --server --port 3000

# Test with specific host binding
python -m src.main --server --host 192.168.1.100 --port 8080
```

## Comparison with Direct Web Server

| Method | Command | Use Case |
|--------|---------|----------|
| **CLI Server Option** | `python -m src.main --server` | Unified entry point, consistent argument handling |
| **Direct Web Server** | `python -m src.web_server` | Direct access to web server, more web-specific options |

### When to Use CLI Server Option

- ✅ You want a single entry point for both CLI and web functionality
- ✅ You prefer consistent argument handling across modes
- ✅ You're using the tool in scripts or automation
- ✅ You want simplified deployment commands

### When to Use Direct Web Server

- ✅ You need web-server-specific options not available in CLI mode
- ✅ You're developing web-specific features
- ✅ You want to bypass CLI argument parsing

## Integration with Makefile

The Makefile provides convenient shortcuts:

```bash
# Using CLI server option (recommended)
make run-web          # Development mode with --server --reload
make run-web-prod     # Production mode with --server --host 0.0.0.0

# Direct web server (alternative)
make run-web-direct   # Direct web server in development mode
```

## Error Handling

The CLI validates arguments and provides helpful error messages:

```bash
# ❌ This will fail with a clear error message
python -m src.main --host 0.0.0.0 --text "Hello"
# Error: --host, --port, and --reload can only be used with --server

# ❌ This will also fail
python -m src.main --server --file input.txt
# Error: Cannot use --file or --text with --server mode
```

## Benefits

1. **Unified Interface**: Single command for both CLI and web functionality
2. **Consistent Arguments**: Same argument parsing and validation for both modes
3. **Simplified Deployment**: Easier to remember and script
4. **Better Integration**: Seamless switching between CLI and web modes
5. **Argument Forwarding**: Proper forwarding of server-specific arguments

## Technical Implementation

The `--server` option works by:

1. Parsing CLI arguments with `parse_known_args()` to handle both CLI and server arguments
2. Validating argument combinations to prevent invalid usage
3. Reconstructing `sys.argv` with server-specific arguments
4. Calling `web_server.main()` with the reconstructed arguments

This approach ensures that all server functionality remains available while providing a unified entry point.