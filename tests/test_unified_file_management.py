#!/usr/bin/env python3
"""
Test script for the unified file management system

This script tests that all TTS artifacts and outputs are properly organized
in a single temp directory structure with session-based organization.
"""

import asyncio
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_unified_file_manager():
    """Test the unified file manager functionality."""
    print("🗂️  Testing Unified File Management System")
    print("=" * 60)
    
    try:
        from src.file_manager import UnifiedFileManager
        
        # Test 1: Initialize file manager
        print("1. Testing file manager initialization...")
        temp_dir = tempfile.mkdtemp(prefix="tts_test_")
        
        # Reset singleton for testing
        UnifiedFileManager._instance = None
        
        file_manager = UnifiedFileManager(temp_dir)
        print(f"   ✅ Initialized with temp dir: {temp_dir}")
        print(f"   ✅ Session ID: {file_manager.session_id}")
        
        # Test singleton pattern
        print("   Testing singleton pattern...")
        file_manager2 = UnifiedFileManager(temp_dir)
        if file_manager2.session_id == file_manager.session_id:
            print(f"   ✅ Singleton pattern working - same session ID: {file_manager.session_id}")
        else:
            print(f"   ❌ Singleton pattern failed - different session IDs")
            print(f"      First: {file_manager.session_id}")
            print(f"      Second: {file_manager2.session_id}")
        
        # Test 2: Create audio file paths
        print("2. Testing audio file path creation...")
        audio_file1, text_file1 = file_manager.create_audio_file_path("test_audio", 0)
        audio_file2, text_file2 = file_manager.create_audio_file_path("test_audio", 1)
        print(f"   ✅ Audio file 1: {audio_file1}")
        print(f"   ✅ Text file 1: {text_file1}")
        print(f"   ✅ Audio file 2: {audio_file2}")
        print(f"   ✅ Text file 2: {text_file2}")
        
        # Test 3: Create translation file path
        print("3. Testing translation file path creation...")
        translation_file = file_manager.create_translation_file_path("en", "fr")
        print(f"   ✅ Translation file: {translation_file}")
        
        # Test 4: Create cache file path
        print("4. Testing cache file path creation...")
        cache_file = file_manager.create_cache_file_path("voices")
        print(f"   ✅ Cache file: {cache_file}")
        
        # Test 5: Create actual files to test cleanup
        print("5. Testing file creation and tracking...")
        Path(audio_file1).touch()
        Path(text_file1).touch()
        Path(audio_file2).touch()
        Path(text_file2).touch()
        Path(translation_file).touch()
        Path(cache_file).touch()
        
        # Write some test content
        with open(audio_file1, 'w') as f:
            f.write("fake audio data")
        with open(translation_file, 'w') as f:
            f.write("Bonjour le monde")
        
        print(f"   ✅ Created {len(file_manager.created_files)} tracked files")
        
        # Test 6: Check directory structure
        print("6. Testing directory structure...")
        expected_dirs = [
            file_manager.session_dir,
            file_manager.audio_dir,
            file_manager.text_dir,
            file_manager.translation_dir,
            file_manager.cache_dir
        ]
        
        for directory in expected_dirs:
            if directory.exists():
                print(f"   ✅ Directory exists: {directory}")
            else:
                print(f"   ❌ Directory missing: {directory}")
        
        # Test 7: Get session info
        print("7. Testing session info...")
        session_info = file_manager.get_session_info()
        print(f"   ✅ Session info: {len(session_info)} keys")
        print(f"   ✅ Files created: {session_info['files_created']}")
        
        # Test 8: Get disk usage
        print("8. Testing disk usage calculation...")
        disk_usage = file_manager.get_disk_usage()
        print(f"   ✅ Total size: {disk_usage['total_size_mb']} MB")
        print(f"   ✅ File count: {disk_usage['file_count']}")
        
        # Test 9: Web URL generation
        print("9. Testing web URL generation...")
        web_url = file_manager.get_web_audio_url(audio_file1)
        print(f"   ✅ Web URL: {web_url}")
        
        # Test 10: Session cleanup
        print("10. Testing session cleanup...")
        cleanup_count = file_manager.cleanup_session_files()
        print(f"   ✅ Cleaned up {cleanup_count} files")
        
        # Test 11: Old session cleanup
        print("11. Testing old session cleanup...")
        old_cleanup_count = file_manager.cleanup_old_sessions(max_age_hours=0)
        print(f"   ✅ Cleaned up {old_cleanup_count} old sessions")
        
        # Clean up test directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        print("\n🎉 All unified file management tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_integration_with_tts():
    """Test integration with TTS components."""
    print("\n🔗 Testing Integration with TTS Components")
    print("=" * 60)
    
    try:
        # Reset singleton for testing
        from src.file_manager import UnifiedFileManager
        UnifiedFileManager._instance = None
        
        from src.tts_service import TTSService
        
        print("1. Testing TTS service with unified file manager...")
        service = TTSService()
        print(f"   ✅ Service initialized")
        print(f"   ✅ Session ID: {service.unified_file_manager.session_id}")
        
        # Test singleton pattern across components
        from src.main import TTSApplication
        app = TTSApplication()
        
        if app.file_manager.session_id == service.unified_file_manager.session_id:
            print(f"   ✅ Singleton pattern working across components - same session ID")
        else:
            print(f"   ❌ Singleton pattern failed across components - different session IDs")
            print(f"      Service: {service.unified_file_manager.session_id}")
            print(f"      App: {app.file_manager.session_id}")
        
        print("2. Testing web streaming with unified file management...")
        test_text = "This is a test of unified file management."
        
        chunk_count = 0
        file_paths = []
        
        async for audio_file, audio_url, paragraph_text in service.stream_tts_web(test_text):
            chunk_count += 1
            file_paths.append(audio_file)
            print(f"   ✅ Generated chunk {chunk_count}: {audio_url}")
            
            # Verify file is in the correct session directory
            if service.unified_file_manager.session_dir.name in audio_file:
                print(f"      ✅ File in session directory: {service.unified_file_manager.session_dir.name}")
            else:
                print(f"      ❌ File not in session directory: {audio_file}")
        
        print(f"   ✅ Generated {chunk_count} chunks with unified file management")
        
        print("3. Testing session info...")
        session_info = service.unified_file_manager.get_session_info()
        print(f"   ✅ Files created in session: {session_info['files_created']}")
        
        print("4. Testing cleanup...")
        cleanup_count = service.unified_file_manager.cleanup_session_files()
        print(f"   ✅ Cleaned up {cleanup_count} files")
        
        print("\n🎉 TTS integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

