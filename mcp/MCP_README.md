# TTS System MCP Server

This directory contains a Model Context Protocol (MCP) server that exposes the Text-to-Speech system functionality to AI assistants and other MCP clients.

## 🎯 Overview

The TTS MCP Server allows AI assistants to:
- Convert text to speech using high-quality neural voices
- Translate text before synthesis
- Stream TTS for long texts
- Manage voice selection and system configuration
- Monitor system health and clean up files

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install MCP library
pip install mcp

# Install TTS system dependencies (if not already installed)
pip install -r requirements.txt
```

### 2. Run Installation Script

```bash
python install_mcp.py
```

This will:
- ✅ Check all dependencies
- ✅ Configure MCP client settings
- ✅ Test the server functionality
- ✅ Provide next steps

### 3. Manual Configuration (Alternative)

If you prefer manual setup, add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "tts-system": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/tts-project",
      "env": {
        "PYTHONPATH": "/path/to/tts-project/src"
      }
    }
  }
}
```

## 🛠️ Available Tools

### Core TTS Tools

#### `synthesize_speech`
Convert text to speech and return audio file path.

**Parameters:**
- `text` (required): Text to convert to speech
- `voice` (optional): Specific voice name to use
- `language` (optional): Language code for the text
- `target_language` (optional): Translate to this language before synthesis
- `output_prefix` (optional): Prefix for output files

**Example:**
```json
{
  "text": "Hello, this is a test of the TTS system!",
  "voice": "en-US-AriaNeural",
  "target_language": "fr"
}
```

#### `stream_tts_synthesis`
Stream TTS synthesis for long texts (returns multiple audio files).

**Parameters:**
- `text` (required): Text to convert to speech
- `voice` (optional): Voice name to use
- `target_language` (optional): Translate before synthesis
- `output_prefix` (optional): Prefix for output files

#### `translate_text`
Translate text to a target language.

**Parameters:**
- `text` (required): Text to translate
- `target_language` (required): Target language code
- `source_language` (optional): Source language (auto-detect if not specified)

### Voice and Configuration Tools

#### `get_available_voices`
Get list of available TTS voices.

**Parameters:**
- `language_filter` (optional): Filter voices by language code

#### `split_text_chunks`
Split text into chunks suitable for TTS processing.

**Parameters:**
- `text` (required): Text to split
- `max_chunk_size` (optional): Maximum characters per chunk

### System Management Tools

#### `get_system_status`
Get TTS system health and status information.

#### `cleanup_files`
Clean up old TTS files to free disk space.

**Parameters:**
- `max_age_hours` (optional): Maximum age of files to keep (default: 24)

## 📚 Available Resources

### `tts://config`
View current TTS system configuration including:
- Output directories
- Voice settings
- Translation limits
- File paths

### `tts://voices`
Complete list of all available TTS voices with details:
- Voice names
- Languages
- Genders
- Locales

### `tts://status`
Real-time system status including:
- Component health checks
- Session information
- Disk usage
- Error states

## 💡 Usage Examples

### Basic Text-to-Speech

Ask your AI assistant:
> "Use the synthesize_speech tool to convert 'Hello world!' to speech"

### Multi-language Translation + TTS

> "Translate 'Good morning, how are you?' to French and then convert it to speech"

### Voice Selection

> "List available English voices and then use one to synthesize 'Welcome to our service'"

### Long Text Processing

> "Use stream_tts_synthesis to convert this long article to speech: [paste article]"

### System Monitoring

> "Check the TTS system status and clean up files older than 12 hours"

## 🔧 Configuration

### Environment Variables

The MCP server respects the same environment variables as the main TTS system:

- `TTS_OUTPUT_DIRECTORY`: Directory for audio files
- `TTS_VOICE`: Default voice to use
- `TTS_MAX_TRANSLATE_CHARS`: Maximum characters per translation

### Voice Selection

You can specify voices in several ways:
1. **By name**: `"en-US-AriaNeural"`
2. **Auto-selection**: Leave empty for automatic selection
3. **Language-based**: Use `language_filter` in `get_available_voices`

### Output Files

Generated audio files are organized in session-based directories:
```
temp/
├── session_20241201_143022_abc123/
│   ├── audio/
│   │   ├── mcp_tts_20241201_143022_000001.wav
│   │   └── mcp_stream_20241201_143025_000001.wav
│   ├── text/
│   │   └── mcp_tts_20241201_143022_000001.txt
│   └── translation/
│       └── translation_auto_to_fr_20241201_143022.txt
```

## 🐛 Troubleshooting

### Common Issues

#### "MCP library not found"
```bash
pip install mcp
```

#### "Failed to import TTS components"
```bash
# Make sure you're in the project root
cd /path/to/tts-project
python install_mcp.py
```

#### "No voices available"
The system will automatically download voices on first use. This requires an internet connection.

#### "Audio files not found"
Check the `temp/` directory and ensure the TTS system has write permissions.

### Debug Mode

Enable verbose logging by setting:
```bash
export TTS_VERBOSE=1
```

### Health Check

Use the `get_system_status` tool to check:
- Component health
- File system status
- Configuration issues

## 🔒 Security Considerations

### File Access
- The MCP server only accesses files within the configured output directory
- Generated files are automatically cleaned up based on age
- No access to system files outside the project directory

### Network Access
- Translation requires internet access to Google Translate
- Voice downloading requires internet access to Microsoft Edge TTS
- No other external network connections

### Resource Usage
- Audio files can be large for long texts
- Automatic cleanup prevents disk space issues
- Memory usage scales with text length

## 🚀 Advanced Usage

### Custom Voice Configuration

Create a custom voice mapping:
```python
# In your MCP client
voice_mapping = {
    "narrator": "en-US-GuyNeural",
    "assistant": "en-US-AriaNeural", 
    "announcer": "en-US-DavisNeural"
}
```

### Batch Processing

Process multiple texts efficiently:
```python
texts = ["Text 1", "Text 2", "Text 3"]
for i, text in enumerate(texts):
    synthesize_speech(text=text, output_prefix=f"batch_{i}")
```

### Integration with Other Tools

Combine with other MCP tools:
1. Use a web scraping tool to get text
2. Use TTS to convert to speech
3. Use file management tools to organize results

## 📈 Performance Tips

### For Long Texts
- Use `stream_tts_synthesis` instead of `synthesize_speech`
- Consider splitting very long texts manually
- Use appropriate chunk sizes for your use case

### Voice Caching
- Voices are cached after first download
- Use consistent voice names for better performance
- Clear cache if experiencing voice issues

### File Management
- Regular cleanup prevents disk space issues
- Monitor disk usage with `get_system_status`
- Adjust cleanup frequency based on usage

## 🤝 Contributing

To extend the MCP server:

1. Add new tools in `mcp_server.py`
2. Update the tool list in `handle_list_tools()`
3. Implement the handler function
4. Update this documentation
5. Test with the installation script

## 📞 Support

For issues with the MCP server:
1. Check the troubleshooting section
2. Run `python install_mcp.py` to verify setup
3. Use `get_system_status` to check component health
4. Check the main TTS system documentation

The MCP server is built on top of the robust TTS system, so most issues are related to the underlying TTS components rather than the MCP integration itself.