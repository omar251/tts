#!/usr/bin/env python3
"""
MCP Server for Text-to-Speech System

This MCP server exposes the TTS system functionality through standardized tools
that can be used by AI assistants and other MCP clients.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Check for MCP availability
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions, NotificationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
    MCP_AVAILABLE = True
except ImportError:
    print("MCP library not found. For testing without MCP, continuing...")
    MCP_AVAILABLE = False
    
    # Create dummy classes for testing without MCP
    class Server:
        def __init__(self, name): 
            self.name = name
        def list_tools(self): 
            def decorator(func): return func
            return decorator
        def call_tool(self): 
            def decorator(func): return func
            return decorator
        def list_resources(self): 
            def decorator(func): return func
            return decorator
        def read_resource(self): 
            def decorator(func): return func
            return decorator
    
    class Tool:
        def __init__(self, **kwargs): 
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class Resource:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class TextContent:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

# Import TTS components
try:
    from src.main import TTSApplication
    from src.tts_service import TTSService
    from src.file_manager import UnifiedFileManager
    from src.settings import settings
    from src.translator import Translator
    from src.text_processor import TextProcessor
    TTS_AVAILABLE = True
except ImportError as e:
    print(f"Failed to import TTS components: {e}")
    print("Make sure you're running from the project root directory")
    TTS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("tts-system")

# Global TTS service instance
tts_service: Optional[TTSService] = None
tts_app: Optional[TTSApplication] = None

async def init_components():
    """Initialize TTS components for testing."""
    global tts_service, tts_app
    if not TTS_AVAILABLE:
        raise ImportError("TTS components not available")
    
    if tts_service is None:
        tts_service = TTSService()
        tts_app = TTSApplication()
    return tts_service, tts_app

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available TTS tools."""
    return [
        Tool(
            name="synthesize_speech",
            description="Convert text to speech and return audio file path",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to convert to speech"
                    },
                    "voice": {
                        "type": "string",
                        "description": "Optional voice name to use for synthesis",
                        "default": None
                    },
                    "language": {
                        "type": "string", 
                        "description": "Optional language code for the text",
                        "default": None
                    },
                    "target_language": {
                        "type": "string",
                        "description": "Optional target language for translation before synthesis",
                        "default": None
                    },
                    "output_prefix": {
                        "type": "string",
                        "description": "Optional prefix for output files",
                        "default": "mcp_tts"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="translate_text",
            description="Translate text to a target language",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to translate"
                    },
                    "target_language": {
                        "type": "string",
                        "description": "Target language code (e.g., 'en', 'fr', 'es')"
                    },
                    "source_language": {
                        "type": "string",
                        "description": "Source language code (auto-detect if not specified)",
                        "default": "auto"
                    }
                },
                "required": ["text", "target_language"]
            }
        ),
        Tool(
            name="get_available_voices",
            description="Get list of available TTS voices",
            inputSchema={
                "type": "object",
                "properties": {
                    "language_filter": {
                        "type": "string",
                        "description": "Optional language code to filter voices",
                        "default": None
                    }
                }
            }
        ),
        Tool(
            name="split_text_chunks",
            description="Split text into chunks suitable for TTS processing",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to split into chunks"
                    },
                    "max_chunk_size": {
                        "type": "integer",
                        "description": "Maximum characters per chunk",
                        "default": 1000
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="stream_tts_synthesis",
            description="Stream TTS synthesis for long texts (returns multiple audio files)",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to convert to speech"
                    },
                    "voice": {
                        "type": "string",
                        "description": "Optional voice name to use",
                        "default": None
                    },
                    "target_language": {
                        "type": "string",
                        "description": "Optional target language for translation",
                        "default": None
                    },
                    "output_prefix": {
                        "type": "string",
                        "description": "Prefix for output files",
                        "default": "mcp_stream"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="get_system_status",
            description="Get TTS system health and status information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cleanup_files",
            description="Clean up old TTS files to free disk space",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_age_hours": {
                        "type": "integer",
                        "description": "Maximum age of files to keep in hours",
                        "default": 24
                    }
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls."""
    global tts_service, tts_app
    
    # Initialize services if needed
    if tts_service is None:
        await init_components()
    
    try:
        if name == "synthesize_speech":
            return await handle_synthesize_speech(arguments)
        elif name == "translate_text":
            return await handle_translate_text(arguments)
        elif name == "get_available_voices":
            return await handle_get_available_voices(arguments)
        elif name == "split_text_chunks":
            return await handle_split_text_chunks(arguments)
        elif name == "stream_tts_synthesis":
            return await handle_stream_tts_synthesis(arguments)
        elif name == "get_system_status":
            return await handle_get_system_status(arguments)
        elif name == "cleanup_files":
            return await handle_cleanup_files(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        logger.error(f"Error handling tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def handle_synthesize_speech(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle speech synthesis."""
    text = arguments["text"]
    voice = arguments.get("voice")
    language = arguments.get("language")
    target_language = arguments.get("target_language")
    output_prefix = arguments.get("output_prefix", "mcp_tts")
    
    logger.info(f"Synthesizing speech for text: {text[:50]}...")
    
    # Translate if requested
    if target_language:
        translator = Translator()
        text = translator.translate_text(text, target_language=target_language)
    
    # Generate audio file path
    file_manager = UnifiedFileManager(settings.output_directory)
    audio_file, text_file = file_manager.create_audio_file_path(output_prefix)
    
    # Set voice if specified
    original_voice = getattr(settings, 'tts_voice', None)
    if voice:
        settings.tts_voice = voice
    
    try:
        # Generate TTS
        result_audio, result_text = await tts_app.tts_generator.generate_tts(
            text, audio_file, text_file
        )
        
        if result_audio and os.path.exists(result_audio):
            file_size = os.path.getsize(result_audio)
            result = {
                "success": True,
                "audio_file": result_audio,
                "text_file": result_text,
                "file_size_bytes": file_size,
                "text_synthesized": text,
                "voice_used": voice or "auto-selected"
            }
            
            return [TextContent(
                type="text", 
                text=f"Speech synthesis completed successfully!\n\n{json.dumps(result, indent=2)}"
            )]
        else:
            return [TextContent(
                type="text",
                text="Speech synthesis failed - no audio file generated"
            )]
    
    finally:
        # Restore original voice
        if voice:
            settings.tts_voice = original_voice

async def handle_translate_text(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle text translation."""
    text = arguments["text"]
    target_language = arguments["target_language"]
    source_language = arguments.get("source_language", "auto")
    
    logger.info(f"Translating text to {target_language}")
    
    translator = Translator()
    if source_language != "auto":
        # Note: The current Translator class doesn't support source_language parameter
        # This is a limitation that could be enhanced in the future
        translated_text = translator.translate_text(text, target_language=target_language)
    else:
        translated_text = translator.translate_text(text, target_language=target_language)
    
    result = {
        "original_text": text,
        "translated_text": translated_text,
        "source_language": source_language,
        "target_language": target_language
    }
    
    return [TextContent(
        type="text",
        text=f"Translation completed!\n\n{json.dumps(result, indent=2)}"
    )]

async def handle_get_available_voices(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle getting available voices."""
    language_filter = arguments.get("language_filter")
    
    logger.info("Fetching available voices")
    
    voices = await tts_service.get_available_voices()
    
    if language_filter:
        voices = [v for v in voices if v.get("Language", "").startswith(language_filter)]
    
    # Format voices for display
    voice_summary = []
    for voice in voices[:20]:  # Limit to first 20 for readability
        voice_info = {
            "name": voice.get("Name", "Unknown"),
            "language": voice.get("Language", "Unknown"),
            "gender": voice.get("Gender", "Unknown"),
            "locale": voice.get("Locale", "Unknown")
        }
        voice_summary.append(voice_info)
    
    result = {
        "total_voices": len(voices),
        "filtered_voices": len(voice_summary),
        "language_filter": language_filter,
        "sample_voices": voice_summary
    }
    
    return [TextContent(
        type="text",
        text=f"Available voices:\n\n{json.dumps(result, indent=2)}"
    )]

async def handle_split_text_chunks(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle text chunking."""
    text = arguments["text"]
    max_chunk_size = arguments.get("max_chunk_size", 1000)
    
    logger.info(f"Splitting text into chunks (max size: {max_chunk_size})")
    
    text_processor = TextProcessor()
    chunks = text_processor.split_text_into_chunks(text)
    
    # Filter chunks by size if needed
    if max_chunk_size:
        filtered_chunks = []
        for chunk in chunks:
            if len(chunk) <= max_chunk_size:
                filtered_chunks.append(chunk)
            else:
                # Split large chunks further
                words = chunk.split()
                current_chunk = ""
                for word in words:
                    if len(current_chunk + " " + word) <= max_chunk_size:
                        current_chunk += " " + word if current_chunk else word
                    else:
                        if current_chunk:
                            filtered_chunks.append(current_chunk)
                        current_chunk = word
                if current_chunk:
                    filtered_chunks.append(current_chunk)
        chunks = filtered_chunks
    
    result = {
        "original_length": len(text),
        "num_chunks": len(chunks),
        "max_chunk_size": max_chunk_size,
        "chunks": chunks
    }
    
    return [TextContent(
        type="text",
        text=f"Text chunking completed:\n\n{json.dumps(result, indent=2)}"
    )]

async def handle_stream_tts_synthesis(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle streaming TTS synthesis."""
    text = arguments["text"]
    voice = arguments.get("voice")
    target_language = arguments.get("target_language")
    output_prefix = arguments.get("output_prefix", "mcp_stream")
    
    logger.info(f"Starting streaming TTS synthesis for text: {text[:50]}...")
    
    audio_files = []
    chunk_count = 0
    
    try:
        async for audio_file, audio_url, paragraph_text in tts_service.stream_tts_web(
            text, voice, None, target_language, client_id=999  # Use special MCP client ID
        ):
            chunk_count += 1
            if os.path.exists(audio_file):
                file_size = os.path.getsize(audio_file)
                audio_files.append({
                    "chunk_number": chunk_count,
                    "audio_file": audio_file,
                    "audio_url": audio_url,
                    "text": paragraph_text[:100] + "..." if len(paragraph_text) > 100 else paragraph_text,
                    "file_size_bytes": file_size
                })
        
        result = {
            "success": True,
            "total_chunks": chunk_count,
            "audio_files": audio_files,
            "original_text_length": len(text)
        }
        
        return [TextContent(
            type="text",
            text=f"Streaming TTS synthesis completed!\n\n{json.dumps(result, indent=2)}"
        )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Streaming TTS synthesis failed: {str(e)}"
        )]

async def handle_get_system_status(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle system status check."""
    logger.info("Checking system status")
    
    # Get health check from TTS service
    health_status = await tts_service.health_check()
    
    # Get file manager info
    file_manager = UnifiedFileManager(settings.output_directory)
    session_info = file_manager.get_session_info()
    disk_usage = file_manager.get_disk_usage()
    
    # Combine all status information
    status = {
        "health": health_status,
        "session": session_info,
        "disk_usage": disk_usage,
        "settings": {
            "output_directory": settings.output_directory,
            "input_file": settings.input_file,
            "max_translate_chars": settings.max_translate_chars
        }
    }
    
    return [TextContent(
        type="text",
        text=f"System status:\n\n{json.dumps(status, indent=2)}"
    )]

async def handle_cleanup_files(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle file cleanup."""
    max_age_hours = arguments.get("max_age_hours", 24)
    
    logger.info(f"Cleaning up files older than {max_age_hours} hours")
    
    cleanup_count = await tts_service.cleanup_old_files(max_age_hours)
    
    result = {
        "files_cleaned": cleanup_count,
        "max_age_hours": max_age_hours,
        "cleanup_time": str(asyncio.get_event_loop().time())
    }
    
    return [TextContent(
        type="text",
        text=f"Cleanup completed:\n\n{json.dumps(result, indent=2)}"
    )]

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="tts://config",
            name="TTS Configuration",
            description="Current TTS system configuration",
            mimeType="application/json"
        ),
        Resource(
            uri="tts://voices",
            name="Available Voices",
            description="List of all available TTS voices",
            mimeType="application/json"
        ),
        Resource(
            uri="tts://status",
            name="System Status",
            description="Current system health and status",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Handle resource reading."""
    global tts_service
    
    if tts_service is None:
        await init_components()
    
    if uri == "tts://config":
        config = {
            "output_directory": settings.output_directory,
            "input_file": settings.input_file,
            "translated_file": settings.translated_file,
            "special_characters": settings.special_characters,
            "delimiter": settings.delimiter,
            "tts_voice": settings.tts_voice,
            "max_translate_chars": settings.max_translate_chars
        }
        return json.dumps(config, indent=2)
    
    elif uri == "tts://voices":
        voices = await tts_service.get_available_voices()
        return json.dumps(voices, indent=2)
    
    elif uri == "tts://status":
        status = await tts_service.health_check()
        return json.dumps(status, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

async def main():
    """Main MCP server entry point."""
    if not MCP_AVAILABLE:
        print("MCP library not available. Cannot run MCP server.")
        print("Install with: pip install mcp")
        return
        
    logger.info("Starting TTS MCP Server...")
    
    # Initialize TTS components
    await init_components()
    logger.info("TTS components initialized successfully")
    
    # Run the MCP server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="tts-system",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(
                        resources_changed=False
                    ),
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())