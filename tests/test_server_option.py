#!/usr/bin/env python3
"""
Test script for the CLI --server option

This script tests that the --server option works correctly and integrates
properly with the web server functionality.
"""

import asyncio
import sys
import os
import subprocess
import time
import requests
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_server_option_help():
    """Test that --server option appears in help."""
    print("1. Testing --server option in help...")
    
    result = subprocess.run([
        sys.executable, "-m", "src.main", "--help"
    ], capture_output=True, text=True)
    
    if "--server" in result.stdout:
        print("   ✅ --server option found in help")
    else:
        print("   ❌ --server option not found in help")
        return False
    
    if "Run the web server instead of CLI mode" in result.stdout:
        print("   ✅ --server help text found")
    else:
        print("   ❌ --server help text not found")
        return False
    
    return True

def test_server_option_validation():
    """Test argument validation for --server option."""
    print("2. Testing argument validation...")
    
    # Test 1: Using server-only args without --server
    result = subprocess.run([
        sys.executable, "-m", "src.main", "--host", "0.0.0.0", "--text", "Hello"
    ], capture_output=True, text=True)
    
    if result.returncode != 0 and "can only be used with --server" in result.stderr:
        print("   ✅ Validation prevents server args without --server")
    else:
        print("   ❌ Validation failed for server args without --server")
        return False
    
    # Test 2: Using CLI args with --server
    result = subprocess.run([
        sys.executable, "-m", "src.main", "--server", "--file", "test.txt"
    ], capture_output=True, text=True)
    
    if result.returncode != 0 and "Cannot use --file or --text with --server mode" in result.stderr:
        print("   ✅ Validation prevents CLI args with --server")
    else:
        print("   ❌ Validation failed for CLI args with --server")
        return False
    
    return True

def test_server_startup():
    """Test that --server option starts the web server."""
    print("3. Testing server startup...")
    
    # Start server in background
    process = subprocess.Popen([
        sys.executable, "-m", "src.main", "--server", "--port", "8001"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a bit for server to start
    time.sleep(3)
    
    try:
        # Test if server is responding
        response = requests.get("http://localhost:8001/api/health", timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Server started and responding to health check")
            health_data = response.json()
            if "status" in health_data:
                print(f"   ✅ Health check returned status: {health_data['status']}")
            success = True
        else:
            print(f"   ❌ Server responded with status code: {response.status_code}")
            success = False
    
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Failed to connect to server: {e}")
        success = False
    
    finally:
        # Clean up: terminate the server process
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    return success

def test_server_with_custom_args():
    """Test server with custom host and port arguments."""
    print("4. Testing server with custom arguments...")
    
    # Start server with custom port
    process = subprocess.Popen([
        sys.executable, "-m", "src.main", "--server", "--host", "127.0.0.1", "--port", "8002", "--verbose"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a bit for server to start
    time.sleep(3)
    
    try:
        # Test if server is responding on custom port
        response = requests.get("http://127.0.0.1:8002/api/health", timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Server started with custom host and port")
            success = True
        else:
            print(f"   ❌ Server responded with status code: {response.status_code}")
            success = False
    
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Failed to connect to server on custom port: {e}")
        success = False
    
    finally:
        # Clean up: terminate the server process
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    return success

def main():
    """Run all tests."""
    print("🖥️  CLI --server Option Test Suite")
    print("Testing the unified CLI entry point for web server")
    print("=" * 60)
    
    # Run tests
    help_success = test_server_option_help()
    validation_success = test_server_option_validation()
    startup_success = test_server_startup()
    custom_args_success = test_server_with_custom_args()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Help Text: {'✅ PASS' if help_success else '❌ FAIL'}")
    print(f"Argument Validation: {'✅ PASS' if validation_success else '❌ FAIL'}")
    print(f"Server Startup: {'✅ PASS' if startup_success else '❌ FAIL'}")
    print(f"Custom Arguments: {'✅ PASS' if custom_args_success else '❌ FAIL'}")
    
    all_passed = all([help_success, validation_success, startup_success, custom_args_success])
    
    if all_passed:
        print("\n🎉 All tests passed! The --server option is working correctly.")
        print("\n✨ Benefits of the --server option:")
        print("   • Unified entry point for both CLI and web functionality")
        print("   • Consistent argument parsing and validation")
        print("   • Simplified deployment and scripting")
        print("   • Better integration between CLI and web modes")
        return 0
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)