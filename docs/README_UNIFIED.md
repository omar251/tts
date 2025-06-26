# Unified Text-to-Speech System

A comprehensive text-to-speech solution that provides both command-line and web interfaces, powered by the same high-quality streaming TTS engine.

## 🎯 Overview

This unified TTS system combines:
- **CLI Tool**: Full-featured command-line interface with streaming TTS
- **Web Interface**: Modern web UI with real-time streaming capabilities
- **API Server**: RESTful API for programmatic access
- **Unified Backend**: All interfaces use the same core TTS components

## 🌟 Features

### Core TTS Capabilities
- **Real-time Streaming**: Audio plays as it's generated, no waiting
- **Intelligent Chunking**: Smart text splitting for natural speech flow
- **Translation Support**: Translate text before synthesis
- **Voice Selection**: 300+ neural voices from Microsoft Edge TTS
- **High Quality**: Natural-sounding speech synthesis

### Multiple Interfaces
- **🖥️ CLI**: Perfect for automation, scripts, and power users
- **🌐 Web**: User-friendly interface for interactive use
- **📡 API**: RESTful endpoints for integration with other services
- **🔌 WebSocket**: Real-time streaming for web applications

### Production Ready
- **Docker Support**: Easy deployment and scaling
- **Health Monitoring**: Built-in health checks and monitoring
- **Error Handling**: Comprehensive error management
- **Resource Management**: Automatic cleanup and optimization

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd tts

# Install dependencies
pip install -r requirements.txt
```

### 2. CLI Usage

```bash
# Basic text-to-speech
python -m src.main -t "Hello world!"

# With translation
python -m src.main -t "Bonjour le monde" -l en

# From file
python -m src.main -f examples/input.txt

# Verbose mode
python -m src.main -t "Hello world!" --verbose
```

### 3. Web Interface

```bash
# Start web server
make run-web
# or
python -m src.web_server --reload

# Open browser
open http://localhost:8000
```

### 4. API Usage

```bash
# Start API server
make run-api
# or
uvicorn src.api_server:app --reload

# Basic synthesis
curl -X POST http://localhost:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!"}'

# With translation
curl -X POST http://localhost:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Bonjour!", "language": "en"}'
```

## 📋 Available Commands

### Make Commands
```bash
make help              # Show all available commands
make run-example       # Run CLI example
make run-api          # Start basic API server
make run-web          # Start unified web server
make run-web-prod     # Start web server (production)
make test             # Run tests
make lint             # Code linting
make format           # Code formatting
```

### Direct Python Commands
```bash
# CLI interface
python -m src.main [options]

# Web server
python -m src.web_server [options]

# API server
uvicorn src.api_server:app [options]
```

## 🌐 Web Interface Features

### Real-Time Streaming
- **Immediate Playback**: Audio starts playing as soon as first chunk is ready
- **Progress Tracking**: Visual feedback on processing status
- **Paragraph Processing**: Text split into natural speech segments

### Voice Selection
- **300+ Voices**: Access to Microsoft's complete neural voice library
- **Language Detection**: Automatic voice selection based on text language
- **Custom Selection**: Choose specific voices for different effects

### User Experience
- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Audio Controls**: Play, pause, volume, speed controls
- **Real-time Updates**: WebSocket-based live updates
- **Mobile Friendly**: Works on desktop, tablet, and mobile

## 📡 API Endpoints

### Basic API (Compatible)
```
POST /synthesize          # Basic TTS synthesis
GET  /docs               # API documentation
```

### Unified Web API
```
GET  /                   # Web interface
GET  /api/voices         # Available voices
GET  /api/health         # Health check
GET  /api/stats          # Service statistics
POST /api/tts/stream     # Streaming TTS
WS   /ws/{client_id}     # WebSocket connection
POST /api/cleanup        # Clean old files
```

## 🐳 Docker Deployment

### Single Service
```bash
# Build image
docker build -t tts-unified .

# Run web interface
docker run -p 8000:8000 tts-unified

# Run API only
docker run -p 8000:8000 tts-unified uvicorn src.api_server:app --host 0.0.0.0
```

### Multi-Service with Docker Compose
```bash
# Start all services
docker-compose up

# Services available:
# - Web Interface: http://localhost:8000
# - API Server: http://localhost:8001
```

## ⚙️ Configuration

### Environment Variables
```bash
TTS_OUTPUT_DIRECTORY=/path/to/output
TTS_INPUT_FILE=/path/to/input.txt
TTS_TRANSLATED_FILE=/path/to/translated.txt
TTS_VOICE=en-US-AriaNeural
```

### Configuration File
Edit `config.yaml`:
```yaml
output_directory: "output_files"
input_file: "examples/input.txt"
translated_file: "output_files/translated.txt"
tts_voice: ""  # Auto-select
```

## 🔧 Architecture

### Unified Service Layer
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Interface │    │  Web Interface  │    │   API Server    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     TTS Service Layer     │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    CLI TTS Components     │
                    │  ┌─────────────────────┐  │
                    │  │   TTSApplication    │  │
                    │  │   ├─ TTS Generator  │  │
                    │  │   ├─ Translator     │  │
                    │  │   ├─ Text Processor │  │
                    │  │   ├─ Audio Player   │  │
                    │  │   └─ File Manager   │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
```

### Data Flow
```
Text Input → Translation (optional) → Text Chunking → TTS Generation → Output
     ↓              ↓                      ↓              ↓           ↓
   CLI/Web      Translator         TextProcessor    TTSGenerator   CLI/Web/API
```

## 🧪 Testing

### Manual Testing
```bash
# Test CLI
python -m src.main -t "Test CLI streaming" --verbose

# Test Web (start server first)
curl http://localhost:8000/

# Test API
curl -X POST http://localhost:8000/synthesize \
  -d '{"text": "Test API"}'
```

### Health Checks
```bash
# Web server health
curl http://localhost:8000/api/health

# API server health
curl http://localhost:8000/docs
```

## 🔍 Troubleshooting

### Common Issues

1. **Server won't start**
   ```bash
   # Check if port is in use
   lsof -i :8000
   
   # Use different port
   python -m src.web_server --port 8001
   ```

2. **Audio not generating**
   ```bash
   # Check health
   curl http://localhost:8000/api/health
   
   # Check logs
   python -m src.web_server --log-level debug
   ```

3. **WebSocket connection issues**
   ```bash
   # Check browser console for errors
   # Ensure WebSocket support is enabled
   ```

### Debug Mode
```bash
# Enable verbose logging
python -m src.web_server --log-level debug

# CLI verbose mode
python -m src.main -t "Debug test" --verbose
```

## 📈 Performance

### Streaming Benefits
- **Immediate Feedback**: Audio starts in 0.5-2 seconds
- **Memory Efficient**: Processes chunks, not entire text
- **Scalable**: Handles very long documents
- **Concurrent**: Multiple requests processed simultaneously

### Optimization Tips
- Use paragraph breaks for better chunking
- Select appropriate voices for target language
- Clean up old files regularly
- Monitor resource usage in production

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run in development mode
make run-web  # Auto-reload enabled

# Code formatting
make format

# Linting
make lint
```

### Adding Features
1. CLI features: Modify `src/main.py` and related components
2. Web features: Update `src/web_server.py` and `static/index.html`
3. API features: Enhance `src/api_server.py`
4. Core features: Update `src/tts_service.py`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Microsoft Edge TTS for high-quality neural voices
- FastAPI for the excellent web framework
- The open-source community for inspiration and tools

---

**Ready to get started?** Choose your preferred interface and start converting text to speech! 🎵