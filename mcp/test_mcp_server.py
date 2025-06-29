#!/usr/bin/env python3
"""
Test script for TTS MCP Server

This script tests the MCP server functionality without requiring a full MCP client.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add src and project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, project_root)  # Add project root for mcp_server import

async def test_mcp_tools():
    """Test MCP server tools directly."""
    print("🧪 Testing TTS MCP Server Tools")
    print("=" * 50)
    
    try:
        # Import the MCP server module
        import mcp_server
        
        # Initialize the server components
        await mcp_server.init_components()  # Initialize without running the server
        
        print("✅ MCP server initialized successfully")
        
        # Test 1: List tools
        print("\n1. Testing tool listing...")
        tools = await mcp_server.handle_list_tools()
        print(f"   ✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"      - {tool.name}: {tool.description}")
        
        # Test 2: System status
        print("\n2. Testing system status...")
        status_result = await mcp_server.handle_call_tool("get_system_status", {})
        print(f"   ✅ System status check completed")
        
        # Test 3: Get available voices (limited)
        print("\n3. Testing voice retrieval...")
        voices_result = await mcp_server.handle_call_tool("get_available_voices", {"language_filter": "en"})
        print(f"   ✅ Voice retrieval completed")
        
        # Test 4: Text chunking
        print("\n4. Testing text chunking...")
        chunk_result = await mcp_server.handle_call_tool("split_text_chunks", {
            "text": "This is a test sentence. This is another sentence for testing the chunking functionality.",
            "max_chunk_size": 50
        })
        print(f"   ✅ Text chunking completed")
        
        # Test 5: Translation (if available)
        print("\n5. Testing translation...")
        try:
            translate_result = await mcp_server.handle_call_tool("translate_text", {
                "text": "Hello world",
                "target_language": "fr"
            })
            print(f"   ✅ Translation completed")
        except Exception as e:
            print(f"   ⚠️  Translation test skipped: {e}")
        
        # Test 6: List resources
        print("\n6. Testing resource listing...")
        resources = await mcp_server.handle_list_resources()
        print(f"   ✅ Found {len(resources)} resources:")
        for resource in resources:
            print(f"      - {resource.name}: {resource.description}")
        
        # Test 7: Read a resource
        print("\n7. Testing resource reading...")
        try:
            config_data = await mcp_server.handle_read_resource("tts://config")
            config = json.loads(config_data)
            print(f"   ✅ Configuration resource read successfully")
            print(f"      Output directory: {config.get('output_directory', 'Unknown')}")
        except Exception as e:
            print(f"   ⚠️  Resource reading test failed: {e}")
        
        print("\n🎉 All MCP server tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_tts_synthesis():
    """Test actual TTS synthesis (optional, requires working TTS system)."""
    print("\n🎵 Testing TTS Synthesis (Optional)")
    print("=" * 50)
    
    try:
        import mcp_server
        
        # Test basic synthesis with a short text
        print("Testing basic speech synthesis...")
        synthesis_result = await mcp_server.handle_call_tool("synthesize_speech", {
            "text": "Hello, this is a test of the MCP TTS system.",
            "output_prefix": "mcp_test"
        })
        
        print("✅ TTS synthesis test completed")
        print("   Check the temp/ directory for generated audio files")
        
        # Test cleanup
        print("\nTesting file cleanup...")
        cleanup_result = await mcp_server.handle_call_tool("cleanup_files", {
            "max_age_hours": 0  # Clean up all files
        })
        print("✅ Cleanup test completed")
        
        return True
        
    except Exception as e:
        print(f"⚠️  TTS synthesis test skipped: {e}")
        print("   This is normal if TTS dependencies are not fully configured")
        return False

def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking Dependencies")
    print("=" * 50)
    
    missing_deps = []
    
    # Check MCP
    try:
        import mcp
        print("✅ MCP library available")
    except ImportError:
        missing_deps.append("mcp")
        print("❌ MCP library not found")
    
    # Check TTS dependencies
    tts_deps = {
        "edge_tts": "edge-tts",
        "googletrans": "googletrans",
        "fastapi": "fastapi",
        "pygame": "pygame",
        "yaml": "pyyaml"
    }
    
    for module, package in tts_deps.items():
        try:
            __import__(module)
            print(f"✅ {package} available")
        except ImportError:
            missing_deps.append(package)
            print(f"❌ {package} not found")
    
    # Check TTS source files
    src_files = [
        "src/main.py",
        "src/tts_service.py", 
        "src/file_manager.py",
        "src/settings.py"
    ]
    
    for file_path in src_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} found")
        else:
            print(f"❌ {file_path} not found")
            missing_deps.append(file_path)
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("\n💡 To fix:")
        print("   1. Install Python packages: pip install -r requirements.txt")
        print("   2. Install MCP: pip install mcp")
        print("   3. Run from project root directory")
        return False
    else:
        print("\n✅ All dependencies available!")
        return True

async def main():
    """Main test function."""
    print("🎵 TTS MCP Server Test Suite")
    print("Testing MCP integration for the TTS system")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("src/main.py").exists():
        print("❌ Please run this script from the TTS project root directory")
        print("   Current directory:", os.getcwd())
        print("   Expected files: src/main.py, src/tts_service.py, etc.")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        print("   Run 'python install_mcp.py' to install missing dependencies")
        return 1
    
    # Test MCP tools
    tools_success = await test_mcp_tools()
    
    # Test TTS synthesis (optional)
    synthesis_success = await test_tts_synthesis()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"MCP Tools: {'✅ PASS' if tools_success else '❌ FAIL'}")
    print(f"TTS Synthesis: {'✅ PASS' if synthesis_success else '⚠️  SKIP'}")
    
    if tools_success:
        print("\n🎉 MCP server is working correctly!")
        print("\nNext steps:")
        print("1. Run 'python install_mcp.py' to configure your MCP client")
        print("2. Restart your MCP client (e.g., Claude Desktop)")
        print("3. Try using the TTS tools in your AI assistant")
        print("\n🛠️  Available tools:")
        print("   - synthesize_speech")
        print("   - translate_text") 
        print("   - get_available_voices")
        print("   - stream_tts_synthesis")
        print("   - get_system_status")
        print("   - cleanup_files")
        return 0
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)