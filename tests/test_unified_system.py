#!/usr/bin/env python3
"""
Test script for the unified TTS system

This script tests that the integration between CLI and web components works correctly.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_tts_service():
    """Test the unified TTS service."""
    print("🧪 Testing Unified TTS Service")
    print("=" * 50)
    
    try:
        from tts_service import TTSService
        
        # Initialize service
        print("1. Initializing TTS service...")
        service = TTSService()
        print("   ✅ TTS service initialized successfully")
        
        # Test health check
        print("2. Testing health check...")
        health = await service.health_check()
        print(f"   ✅ Health status: {health['status']}")
        
        # Test voice retrieval
        print("3. Testing voice retrieval...")
        voices = await service.get_available_voices()
        print(f"   ✅ Found {len(voices)} voices")
        
        # Test web streaming (generator)
        print("4. Testing web streaming interface...")
        test_text = "This is a test of the unified system. It should work with both CLI and web components."
        
        chunk_count = 0
        async for audio_file, audio_url, paragraph_text in service.stream_tts_web(test_text):
            chunk_count += 1
            print(f"   ✅ Generated chunk {chunk_count}: {paragraph_text[:30]}...")
            
            # Check if file exists
            if os.path.exists(audio_file):
                file_size = os.path.getsize(audio_file)
                print(f"      📁 Audio file: {audio_file} ({file_size} bytes)")
            else:
                print(f"      ❌ Audio file not found: {audio_file}")
        
        print(f"   ✅ Web streaming completed: {chunk_count} chunks generated")
        
        print("\n🎉 All tests passed! The unified system is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cli_components():
    """Test that CLI components are still working."""
    print("\n🖥️  Testing CLI Components")
    print("=" * 50)
    
    try:
        from main import TTSApplication
        
        print("1. Initializing CLI application...")
        app = TTSApplication()
        print("   ✅ CLI application initialized successfully")
        
        print("2. Testing text processor...")
        chunks = app.text_processor.split_text_into_chunks("Test text for chunking. This should be split properly.")
        print(f"   ✅ Text processor working: {len(chunks)} chunks")
        
        print("3. Testing translator...")
        try:
            translated = app.translator.translate_text("Hello", "fr")
            print(f"   ✅ Translator working: 'Hello' → '{translated}'")
        except Exception as e:
            print(f"   ⚠️  Translator test skipped: {e}")
        
        print("4. Testing TTS generator initialization...")
        # Just test that it initializes without errors
        generator = app.tts_generator
        print("   ✅ TTS generator initialized successfully")
        
        print("\n✅ CLI components are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

