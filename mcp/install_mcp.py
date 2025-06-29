#!/usr/bin/env python3
"""
Installation script for TTS MCP Server

This script helps set up the MCP server for the TTS system.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def check_mcp_installed():
    """Check if MCP library is installed."""
    try:
        import mcp
        print("✅ MCP library is already installed")
        return True
    except ImportError:
        print("❌ MCP library not found")
        return False

def install_mcp():
    """Install MCP library."""
    print("📦 Installing MCP library...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
        print("✅ MCP library installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install MCP library: {e}")
        return False

def check_tts_dependencies():
    """Check if TTS system dependencies are available."""
    missing_deps = []
    
    try:
        import edge_tts
    except ImportError:
        missing_deps.append("edge-tts")
    
    try:
        import googletrans
    except ImportError:
        missing_deps.append("googletrans")
    
    try:
        import fastapi
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import pygame
    except ImportError:
        missing_deps.append("pygame")
    
    if missing_deps:
        print(f"❌ Missing TTS dependencies: {', '.join(missing_deps)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    else:
        print("✅ All TTS dependencies are available")
        return True

def create_mcp_config():
    """Create or update MCP configuration."""
    config_path = Path.home() / ".config" / "mcp" / "config.json"
    
    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new one
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {"mcpServers": {}}
    
    # Add TTS server configuration
    tts_server_config = {
        "command": "python",
        "args": [str(Path(__file__).parent / "mcp_server.py")],
        "cwd": str(Path(__file__).parent),
        "env": {
            "PYTHONPATH": str(Path(__file__).parent / "src")
        }
    }
    
    config["mcpServers"]["tts-system"] = tts_server_config
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ MCP configuration updated: {config_path}")
    return True

def test_mcp_server():
    """Test the MCP server."""
    print("🧪 Testing MCP server...")
    
    try:
        # Try to import and initialize the server
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        # Test TTS imports
        from src.main import TTSApplication
        from src.tts_service import TTSService
        
        print("✅ TTS components can be imported")
        
        # Test MCP server import
        import mcp_server
        print("✅ MCP server can be imported")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

def main():
    """Main installation function."""
    print("🎵 TTS MCP Server Installation")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src/main.py").exists():
        print("❌ Please run this script from the TTS project root directory")
        sys.exit(1)
    
    # Step 1: Check/install MCP library
    if not check_mcp_installed():
        if not install_mcp():
            print("❌ Installation failed: Could not install MCP library")
            sys.exit(1)
    
    # Step 2: Check TTS dependencies
    if not check_tts_dependencies():
        print("❌ Installation failed: Missing TTS dependencies")
        print("💡 Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 3: Create MCP configuration
    if not create_mcp_config():
        print("❌ Installation failed: Could not create MCP configuration")
        sys.exit(1)
    
    # Step 4: Test the server
    if not test_mcp_server():
        print("❌ Installation failed: MCP server test failed")
        sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Restart your MCP client (e.g., Claude Desktop)")
    print("2. The 'tts-system' server should now be available")
    print("3. Try using tools like 'synthesize_speech' or 'get_available_voices'")
    print("\n🔧 Available tools:")
    print("- synthesize_speech: Convert text to speech")
    print("- translate_text: Translate text to another language")
    print("- get_available_voices: List available TTS voices")
    print("- split_text_chunks: Split text into TTS-friendly chunks")
    print("- stream_tts_synthesis: Stream TTS for long texts")
    print("- get_system_status: Check system health")
    print("- cleanup_files: Clean up old audio files")
    print("\n📚 Resources:")
    print("- tts://config: View current configuration")
    print("- tts://voices: List all available voices")
    print("- tts://status: Check system status")

if __name__ == "__main__":
    main()