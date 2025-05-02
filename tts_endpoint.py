import asyncio
import os
from datetime import datetime
import random
from typing import Optional

import edge_tts
from edge_tts import VoicesManager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
import uvicorn

# --- Constants ---
OUTPUT_DIRECTORY = "output_audio"
STATIC_DIRECTORY = "static"

# --- FastAPI App Setup ---
app = FastAPI()
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
os.makedirs(STATIC_DIRECTORY, exist_ok=True)
app.mount("/audio", StaticFiles(directory=OUTPUT_DIRECTORY), name="audio")
app.mount("/static", StaticFiles(directory=STATIC_DIRECTORY), name="static")

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"Client #{client_id} connected via WebSocket")

    def disconnect(self, client_id: int):
        self.active_connections.pop(client_id, None)
        print(f"Client #{client_id} disconnected")

    async def send_json(self, data: dict, client_id: int):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(data)
            except Exception as e:
                print(f"Error sending to client #{client_id}: {e}")
                self.disconnect(client_id)

manager = ConnectionManager()

# --- Core Functions ---
async def get_voice(voice_name: str = None) -> str:
    """Select a specific voice or a random English voice."""
    if voice_name:
        return voice_name
    try:
        voices = await VoicesManager.create()
        voice_options = voices.find(Language="en")
        if voice_options:
            return random.choice(voice_options)["Name"]
        return "en-US-JennyNeural"
    except Exception as e:
        print(f"Error getting voices: {e}")
        return "en-US-JennyNeural"

async def generate_tts_chunk(text: str, base_filename: str, voice: str) -> str | None:
    """Generate TTS audio for a single text chunk and return the file path."""
    audio_filepath = f"{base_filename}.wav"
    try:
        communicate = edge_tts.Communicate(text, voice)
        with open(audio_filepath, "wb") as audio_f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_f.write(chunk["data"])
        return audio_filepath
    except Exception as e:
        print(f"TTS error for {audio_filepath}: {e}")
        if os.path.exists(audio_filepath):
            os.remove(audio_filepath)
        return None

# --- Input Model ---
class StreamTTSInput(BaseModel):
    text: str
    voice: Optional[str] = None
    client_id: int

    @validator("text")
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        if len(v) > 100_000:
            raise ValueError("Text is too long")
        return v

# --- Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def get_root():
    """Serve the main HTML page."""
    return FileResponse("static/index.html")

@app.get("/api/voices")
async def get_available_voices():
    """Get list of available English TTS voices."""
    try:
        voices = await VoicesManager.create()
        return voices.find(Language="en")
    except Exception as e:
        return {"error": f"Failed to get voices: {str(e)}"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """Handle WebSocket connections for a specific client."""
    await manager.connect(websocket, client_id)
    try:
        while True:
            # This endpoint primarily manages the connection and basic echo.
            # The /api/tts/stream endpoint handles the TTS specific messages.
            # We can keep this simple or add more WebSocket commands if needed later.
            data = await websocket.receive_text()
            print(f"Client #{client_id} sent: {data}")
            # Example: echo back received text
            await manager.send_json({"message": f"You wrote: {data}"}, client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error for client #{client_id}: {e}")
        manager.disconnect(client_id)


@app.post("/api/tts/stream")
async def tts_stream(data: StreamTTSInput):
    """Process text by paragraphs and stream audio URLs and text via WebSocket in order."""
    text = data.text
    voice = data.voice
    client_id = data.client_id
    selected_voice = await get_voice(voice)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    # Split text into paragraphs
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        await manager.send_json({"type": "error", "message": "No valid paragraphs found"}, client_id)
        return {"error": "No valid paragraphs found"}

    # Process chunks with limited concurrency, ensuring ordered delivery
    semaphore = asyncio.Semaphore(2)  # Allow 2 concurrent tasks
    failed_count = 0
    successful_count = 0

    for index, paragraph in enumerate(paragraphs):
        async with semaphore:
            base_filename = os.path.join(OUTPUT_DIRECTORY, f"output_{timestamp}_{index:06d}")
            audio_file = await generate_tts_chunk(paragraph, base_filename, selected_voice)
            if audio_file:
                url = f"/audio/{os.path.basename(audio_file)}"
                # Send both the URL and the paragraph text
                await manager.send_json({"type": "audio_url", "url": url, "text": paragraph}, client_id)
                successful_count += 1
            else:
                failed_count += 1

    # Send completion message
    completion_message = {"type": "complete"}
    if failed_count > 0:
        completion_message["warning"] = f"{failed_count} paragraph(s) failed to process"
    if successful_count == 0:
        completion_message["type"] = "error"
        completion_message["message"] = "No audio files generated"
    await manager.send_json(completion_message, client_id)

    return {"status": "processing_started"}

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting FastAPI server...")
    # Note: Use `uvicorn tts_endpoint:app --reload --host 127.0.0.1 --port 8000` from terminal for development
    uvicorn.run(app, host="0.0.0.0", port=8000)