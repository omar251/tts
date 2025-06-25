# Component Comparison: api_server.py vs tts_service.py vs web_server.py

## 🎯 **Overview**

These three components serve different roles in the unified TTS system:

| Component | Role | Purpose | Interface |
|-----------|------|---------|-----------|
| **`api_server.py`** | Basic API Server | Simple HTTP API for TTS | REST API |
| **`tts_service.py`** | Service Layer | Unified business logic | Internal Library |
| **`web_server.py`** | Advanced Web Server | Full web app with streaming | Web UI + WebSocket |

## 📋 **Detailed Comparison**

### 🔧 **1. api_server.py - Basic API Server**

#### **Purpose**
- Simple REST API for basic TTS functionality
- Compatible with existing API clients
- Minimal, straightforward HTTP endpoints

#### **Key Features**
```python
@app.post("/synthesize")
async def synthesize_text_to_speech(request: SynthesizeRequest):
    # Direct TTS generation
    audio_file, text_file = await tts_generator.generate_tts(text, audio_file, text_file)
    return FileResponse(audio_file)
```

#### **What It Does**
- ✅ **Basic TTS**: Convert text to speech
- ✅ **Translation**: Optional text translation
- ✅ **Voice Selection**: Specify TTS voice
- ✅ **File Response**: Returns complete audio file
- ❌ **No Streaming**: Waits for complete processing
- ❌ **No Web UI**: API only

#### **Usage**
```bash
# Start server
make run-api

# Use API
curl -X POST http://localhost:8000/synthesize \
  -d '{"text": "Hello world!"}' \
  --output speech.wav
```

#### **Architecture**
```
HTTP Request → API Endpoint → TTS Components → Audio File → HTTP Response
```

---

### 🔗 **2. tts_service.py - Unified Service Layer**

#### **Purpose**
- Bridge between CLI and web functionality
- Unified business logic for all interfaces
- Reusable service layer

#### **Key Features**
```python
class TTSService:
    def __init__(self):
        self.tts_app = TTSApplication()  # Uses CLI components

    async def stream_tts_cli(self, text, output_file):
        # CLI streaming logic
        await self.tts_app.talk(text, output_file)

    async def stream_tts_web(self, text, voice):
        # Web streaming logic
        async for audio_file, audio_url, text in self.process_chunks():
            yield audio_file, audio_url, text
```

#### **What It Does**
- ✅ **CLI Integration**: Uses original CLI streaming logic
- ✅ **Web Streaming**: Adapts CLI logic for web use
- ✅ **Unified Interface**: Same TTS quality across all interfaces
- ✅ **Health Monitoring**: System health checks
- ✅ **Voice Management**: Centralized voice handling
- ✅ **Code Reuse**: Single source of TTS logic

#### **Usage**
```python
# Used internally by other components
service = TTSService()

# CLI-style streaming
await service.stream_tts_cli(text, output_file)

# Web-style streaming
async for audio_file, url, text in service.stream_tts_web(text):
    # Process each chunk
```

#### **Architecture**
```
CLI/Web/API → TTSService → TTSApplication (CLI Components) → TTS Output
```

---

### 🌐 **3. web_server.py - Advanced Web Server**

#### **Purpose**
- Full-featured web application
- Real-time streaming TTS interface
- Modern web UI with WebSocket support

#### **Key Features**
```python
@app.get("/")
async def get_root():
    return FileResponse("static/index.html")  # Web UI

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket, client_id):
    # Real-time communication

@app.post("/api/tts/stream")
async def stream_tts_endpoint(request):
    # Uses TTSService for streaming
    async for audio_file, url, text in tts_service.stream_tts_web(text):
        await websocket.send_json({"url": url, "text": text})
```

#### **What It Does**
- ✅ **Web Interface**: Modern, responsive UI
- ✅ **Real-time Streaming**: WebSocket-based streaming
- ✅ **Voice Selection**: 300+ voices with UI
- ✅ **Progress Tracking**: Live updates and status
- ✅ **Mobile Friendly**: Works on all devices
- ✅ **API Compatible**: Includes basic API endpoints
- ✅ **Uses TTSService**: Leverages unified service layer

#### **Usage**
```bash
# Start web server
make run-web

# Access web interface
open http://localhost:8000

# Features:
# - Text input with translation
# - Voice selection dropdown
# - Real-time audio streaming
# - Progress indicators
```

#### **Architecture**
```
Web Browser ↔ WebSocket ↔ Web Server ↔ TTSService ↔ CLI Components
     ↓              ↓           ↓           ↓            ↓
   Web UI    Real-time    FastAPI    Unified     Original TTS
            Updates      Endpoints   Logic       Components
```

## 🔄 **How They Work Together**

### **Layered Architecture**
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   api_server    │  │   web_server    │  │   CLI (main)    │
│   (Basic API)   │  │ (Advanced Web)  │  │  (Original)     │
└─────────┬───────┘  └─────────┬───────┘  └─────────┬───────┘
          │                    │                    │
          │         ┌──────────▼──────────┐         │
          └─────────►│    tts_service     │◄────────┘
                    │  (Unified Logic)    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   CLI Components    │
                    │ (TTSApplication,    │
                    │  TTS Generator,     │
                    │  Translator, etc.)  │
                    └─────────────────────┘
```

### **Data Flow Examples**

#### **Basic API Request**
```
1. HTTP POST /synthesize
2. api_server.py → tts_generator directly
3. Generate complete audio file
4. Return FileResponse
```

#### **Web Streaming Request**
```
1. WebSocket connection + HTTP POST /api/tts/stream
2. web_server.py → tts_service.py
3. tts_service.py → TTSApplication (CLI components)
4. Stream audio URLs back via WebSocket
5. Web UI plays audio in real-time
```

#### **CLI Usage**
```
1. python -m src.main
2. main.py → TTSApplication directly
3. Stream audio to local audio player
4. Immediate local playback
```

## 📊 **Feature Comparison**

| Feature | api_server.py | tts_service.py | web_server.py |
|---------|---------------|----------------|---------------|
| **HTTP API** | ✅ Basic | ❌ No | ✅ Enhanced |
| **Web Interface** | ❌ No | ❌ No | ✅ Modern UI |
| **WebSocket** | ❌ No | ❌ No | ✅ Real-time |
| **Streaming** | ❌ No | ✅ Yes | ✅ Yes |
| **CLI Integration** | ❌ Direct | ✅ Bridge | ✅ Via Service |
| **Voice Selection** | ✅ Basic | ✅ Advanced | ✅ UI Dropdown |
| **Translation** | ✅ Basic | ✅ Advanced | ✅ UI Support |
| **Health Checks** | ❌ No | ✅ Yes | ✅ Yes |
| **File Cleanup** | ✅ Basic | ✅ Advanced | ✅ Advanced |
| **Error Handling** | ✅ Basic | ✅ Comprehensive | ✅ Comprehensive |

## 🎯 **When to Use Each**

### **Use `api_server.py` when:**
- ✅ You need a simple REST API
- ✅ Backward compatibility is important
- ✅ You don't need streaming
- ✅ Integration with existing API clients
- ✅ Minimal resource usage

### **Use `tts_service.py` when:**
- ✅ Building new applications
- ✅ You need unified TTS logic
- ✅ Integrating CLI and web functionality
- ✅ You want code reuse
- ✅ Building custom interfaces

### **Use `web_server.py` when:**
- ✅ You want a complete web application
- ✅ Real-time streaming is needed
- ✅ Non-technical users will use the system
- ✅ You need a modern UI
- ✅ Mobile support is important

## 🚀 **Usage Examples**

### **Starting Each Server**

#### **Basic API Server**
```bash
make run-api
# or
uvicorn src.api_server:app --reload --host 0.0.0.0 --port 8000

# Access: http://localhost:8000/docs
```

#### **Web Server**
```bash
make run-web
# or
python -m src.web_server --reload

# Access: http://localhost:8000
```

#### **Using TTS Service (Programmatically)**
```python
from src.tts_service import TTSService

service = TTSService()

# CLI-style
await service.stream_tts_cli("Hello world!", "output.wav")

# Web-style
async for audio_file, url, text in service.stream_tts_web("Hello world!"):
    print(f"Generated: {url}")
```

## 🎵 **Summary**

- **`api_server.py`**: Simple, backward-compatible REST API
- **`tts_service.py`**: Unified business logic layer that bridges CLI and web
- **`web_server.py`**: Full-featured web application with real-time streaming

All three work together to provide a comprehensive TTS solution that maintains the excellent CLI functionality while adding modern web capabilities!
