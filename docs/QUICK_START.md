# 🚀 Quick Start Guide - Unified TTS System

## ✅ **Setup Restored Successfully!**

Your unified TTS system is now fully restored and ready to use. You have three ways to use the system:

## 🖥️ **1. CLI Interface (Original)**

### Basic Usage
```bash
# Simple text-to-speech
python -m src.main -t "Hello world!"

# With translation
python -m src.main -t "Bonjour le monde" -l en

# From file
python -m src.main -f examples/input.txt

# Verbose mode (see streaming in action)
python -m src.main -t "This is a test of streaming TTS" --verbose
```

### CLI Features
- ✅ **Streaming TTS**: Audio plays immediately as chunks are processed
- ✅ **Translation**: Translate text before synthesis
- ✅ **File input**: Process text files
- ✅ **Voice selection**: Configure in config.yaml
- ✅ **Local playback**: Audio plays directly on your system

## 🌐 **2. Web Interface (New)**

### Start Web Server

#### Option 1: Using CLI --server option (Recommended)
```bash
# Development mode (auto-reload)
make run-web
# or
python -m src.main --server --reload

# Production mode
make run-web-prod
# or
python -m src.main --server --host 0.0.0.0 --port 8000

# Custom configuration
python -m src.main --server --host 0.0.0.0 --port 8080 --verbose
```

#### Option 2: Direct web server
```bash
# Development mode (auto-reload)
make run-web-direct
# or
python -m src.web_server --reload

# Production mode
make run-web-prod-direct
# or
python -m src.web_server --host 0.0.0.0 --port 8000
```

### Access Web Interface
```
Open: http://localhost:8000
```

### Web Features
- ✅ **Modern UI**: Beautiful, responsive web interface
- ✅ **Real-time streaming**: Audio streams as text is processed
- ✅ **Voice selection**: Choose from 300+ voices
- ✅ **Translation**: Built-in translation support
- ✅ **WebSocket**: Live updates and progress tracking
- ✅ **Mobile friendly**: Works on phones and tablets

## 🐳 **3. Docker Deployment**

### Single Service
```bash
# Build image
docker build -t tts-unified .

# Run web interface
docker run -p 8000:8000 tts-unified

# Access at http://localhost:8000
```

## 🔧 **Available Commands**

### Make Commands
```bash
make help              # Show all commands
make run-example       # Test CLI with example
make run-web          # Start web server (dev)
make run-web-prod     # Start web server (prod)
make test             # Run tests
make clean            # Clean up files
```

### Direct Commands
```bash
# CLI
python -m src.main [options]

# Web server
python -m src.web_server [options]

# Verification
python verify_setup.py
```

## 🎯 **Quick Test**

### Test CLI
```bash
python -m src.main -t "Testing CLI streaming" --verbose
```

### Test Web Interface
```bash
# Start server
make run-web

# Open browser
open http://localhost:8000

# Enter text and click "Stream Audio"
```

## 🌟 **Key Features**

### Unified Backend
- ✅ **Same TTS engine**: All interfaces use identical high-quality TTS
- ✅ **Shared components**: CLI components power web and API
- ✅ **Consistent behavior**: Same results across all interfaces

### Streaming Capabilities
- ✅ **CLI streaming**: Immediate local audio playback
- ✅ **Web streaming**: Real-time audio URLs via WebSocket
- ✅ **Smart chunking**: Intelligent text splitting for natural speech

### Production Ready
- ✅ **Docker support**: Easy deployment and scaling
- ✅ **Health monitoring**: Built-in health checks
- ✅ **Error handling**: Comprehensive error management
- ✅ **Resource cleanup**: Automatic file management

## 🔍 **Troubleshooting**

### Common Issues

1. **Port already in use**
   ```bash
   # Use different port
   python -m src.web_server --port 8001
   ```

2. **Dependencies missing**
   ```bash
   pip install -r requirements.txt
   ```

3. **Audio not playing (CLI)**
   ```bash
   # Check audio system
   python -m src.main -t "test" --verbose
   ```

4. **Web interface not loading**
   ```bash
   # Check server status
   curl http://localhost:8000/api/health
   ```

### Debug Mode
```bash
# Web server debug
python -m src.web_server --log-level debug

# CLI verbose
python -m src.main -t "debug test" --verbose
```

## 📚 **Documentation**

- **README_UNIFIED.md**: Comprehensive documentation
- **MERGE_SUMMARY.md**: Technical details of the merge
- **API Docs**: http://localhost:8000/docs (when web server is running)

## 🎉 **You're Ready!**

The unified TTS system is fully restored and operational. Choose your preferred interface:

- **🖥️ CLI**: For automation and power users
- **🌐 Web**: For interactive use and non-technical users, and for API access.
- **🐳 Docker**: For production deployment

All interfaces provide the same high-quality streaming TTS experience! 🎵