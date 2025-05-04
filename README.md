# Text-to-Speech Streaming Service with Real-time Audio Generation

A modern web application that converts text into natural-sounding speech using Microsoft's Edge TTS engine. The service streams audio in real-time, supports multiple voices, and provides an intuitive web interface with advanced audio playback controls.

This project combines FastAPI's high-performance backend with WebSocket communication to deliver a responsive text-to-speech experience. It features paragraph-by-paragraph processing, concurrent audio generation, and a custom audio player with controls for volume, playback speed, and track navigation. The service is containerized for easy deployment and scalability.

## Features

- **Real-time Audio Streaming**: Converts text to speech and streams audio as it's generated
- **Paragraph Processing**: Intelligently splits text into paragraphs for natural-sounding speech
- **Concurrent Generation**: Processes multiple audio segments simultaneously for faster delivery
- **Multiple Voice Support**: Access to Microsoft's extensive neural voice library
- **WebSocket Communication**: Maintains persistent connections for real-time updates
- **Custom Audio Player**: Web interface with playback controls and voice selection
- **Containerized Deployment**: Docker support for easy deployment and scaling

## Repository Structure
```
.
├── Dockerfile              # Container configuration for building and running the application
├── pyproject.toml          # Python project metadata and dependencies
├── requirements.txt        # Generated dependency list for reproducible builds
├── static/
│   └── index.html          # Web interface with custom audio player and controls
├── tts_endpoint.py         # FastAPI application with WebSocket and TTS processing logic
└── uv.lock                 # Dependency lock file for reproducible builds
```

## Usage Instructions
### Prerequisites
- Python 3.12 or higher
- Docker (optional, for containerized deployment)

Required Python packages:
- deep-translator >= 1.11.4
- edge-tts >= 7.0.1
- websockets >= 15.0.1
- fastapi >= 0.111.0
- uvicorn[standard] >= 0.29.0

### Installation

#### Local Installation
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Docker Installation
```bash
# Build the Docker image
docker build -t tts-service .

# Run the container
docker run -p 8000:8000 tts-service
```

### Quick Start
1. Start the server:
```bash
# Local development
uvicorn tts_endpoint:app --reload --host 127.0.0.1 --port 8000

# Production
uvicorn tts_endpoint:app --host 0.0.0.0 --port 8000
```

2. Open `http://localhost:8000` in your web browser
3. Enter text in the textarea
4. Select a voice from the dropdown menu
5. Click "Stream Audio" to begin TTS conversion

### API Endpoints

- `GET /`: Main web interface
- `GET /api/voices`: Returns list of available TTS voices
- `POST /api/tts/stream`: Processes text and streams audio URLs via WebSocket
- `WebSocket /ws/{client_id}`: WebSocket endpoint for real-time communication

#### Debug Mode
Enable debug logging:
```bash
uvicorn tts_endpoint:app --log-level debug
```

## Data Flow
The service processes text-to-speech requests by splitting text into paragraphs and generating audio files concurrently while maintaining order.

```ascii
[Client] -> [WebSocket] -> [TTS Engine]
    |           |              |
    |           |        [Audio Generation]
    |           |              |
    |      [Audio URLs]    [Storage]
    |           |              |
[Audio Player]<-[Stream]<-[Audio Files]
```

Component Interactions:
1. Client establishes WebSocket connection with unique client_id
2. Text is split into paragraphs for processing
3. TTS engine generates audio files concurrently (max 2 simultaneous)
4. Audio files are stored in output_audio directory
5. Audio URLs are streamed to client in order
6. Client audio player loads and plays audio sequentially
7. WebSocket maintains real-time communication for status updates

## License

This project is open source and available under the MIT License.