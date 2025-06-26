#!/usr/bin/env python3
"""
Unified Web Server for TTS

This module provides a web interface that uses the existing CLI TTS components
through the unified TTS service layer. It combines the best of both the main branch
CLI functionality and the webtts branch web interface.
"""

import asyncio
import json
import os
import logging
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
import uvicorn
from PyPDF2 import PdfReader
import re

from .tts_service import TTSService
from .settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App Setup ---
app = FastAPI(
    title="Unified Text-to-Speech Service",
    description="TTS service with both CLI and web interfaces, powered by the same streaming engine",
    version="2.0.0"
)

# Ensure directories exist
os.makedirs(settings.output_directory, exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/audio", StaticFiles(directory=settings.output_directory), name="audio")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize TTS service
tts_service = TTSService()

# --- WebSocket Connection Manager ---
class ConnectionManager:
    """Manages WebSocket connections for real-time communication."""
    
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: int):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client #{client_id} connected via WebSocket")
    
    def disconnect(self, client_id: int):
        """Remove a WebSocket connection."""
        self.active_connections.pop(client_id, None)
        logger.info(f"Client #{client_id} disconnected")
    
    async def send_json(self, data: Dict[Any, Any], client_id: int):
        """Send JSON data to a specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(data)
            except Exception as e:
                logger.error(f"Error sending to client #{client_id}: {e}")
                self.disconnect(client_id)

manager = ConnectionManager()

# --- Request Models ---
class BasicTTSRequest(BaseModel):
    """Request model for basic TTS synthesis (compatible with existing API)."""
    text: str
    language: Optional[str] = None
    voice: Optional[str] = None
    
    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v

class StreamTTSRequest(BaseModel):
    """Request model for streaming TTS synthesis."""
    text: str
    voice: Optional[str] = None
    language: Optional[str] = None
    target_language: Optional[str] = None # New field for translation
    client_id: int
    
    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        if len(v) > 100_000:
            raise ValueError("Text is too long (max 100,000 characters)")
        return v

# --- Web Interface Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def get_root():
    """Serve the main web interface."""
    try:
        return FileResponse("static/index.html")
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <head><title>TTS Service</title></head>
            <body>
                <h1>TTS Service is Running</h1>
                <p>Web interface not available. Use API endpoints:</p>
                <ul>
                    <li><a href="/docs">API Documentation</a></li>
                    <li><a href="/api/voices">Available Voices</a></li>
                </ul>
            </body>
        </html>
        """)

# --- API Endpoints ---
@app.post("/synthesize")
async def basic_synthesize(request: BasicTTSRequest):
    """
    Basic TTS synthesis endpoint (compatible with existing API).
    
    This endpoint maintains compatibility with the existing API while using
    the unified TTS service layer that leverages CLI components.
    """
    try:
        logger.info(f"Basic TTS request: {request.text[:50]}...")
        
        # Use unified file manager for consistent file paths
        audio_file, text_file = tts_service.unified_file_manager.create_audio_file_path("basic_tts")
        
        # Use TTS service with CLI components
        if request.voice:
            # Temporarily set voice
            original_voice = getattr(settings, 'tts_voice', None)
            settings.tts_voice = request.voice
        
        try:
            # Use the CLI TTS generator through the service
            result_audio, result_text = await tts_service.tts_app.tts_generator.generate_tts(
                request.text, audio_file, text_file
            )
            
            if not result_audio or not os.path.exists(result_audio):
                raise HTTPException(status_code=500, detail="TTS generation failed")
            
            # Return the audio file
            media_type = "audio/wav"
            filename = "speech.wav"
            
            return FileResponse(
                path=result_audio,
                media_type=media_type,
                filename=filename
            )
        
        finally:
            # Restore original voice setting
            if request.voice and 'original_voice' in locals():
                settings.tts_voice = original_voice
    
    except Exception as e:
        logger.error(f"Basic TTS synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/voices")
async def get_available_voices():
    """Get list of available TTS voices using CLI components."""
    try:
        voices = await tts_service.get_available_voices()
        return voices
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        return {"error": f"Failed to get voices: {str(e)}"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint using the unified service."""
    return await tts_service.health_check()

@app.get("/api/translation_languages")
async def get_available_translation_languages():
    """Get list of available translation languages.

    This is a simplified list for demonstration. In a real application,
    this might be dynamically fetched from a translation service.
    """
    # This list can be expanded or fetched dynamically from a translation API
    languages = [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "it", "name": "Italian"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "zh-CN", "name": "Chinese (Simplified)"},
        {"code": "ja", "name": "Japanese"},
        {"code": "ko", "name": "Korean"},
        {"code": "ru", "name": "Russian"},
        {"code": "ar", "name": "Arabic"},
        {"code": "hi", "name": "Hindi"},
    ]
    return languages

# --- WebSocket Endpoints ---
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """Handle WebSocket connections for real-time communication."""
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Client #{client_id} sent: {data}")
            
            # Echo back for basic connectivity testing
            await manager.send_json({"message": f"Echo: {data}"}, client_id)
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client #{client_id}: {e}")
        manager.disconnect(client_id)

@app.post("/api/tts/stream")
async def stream_tts_endpoint(request: StreamTTSRequest):
    """
    Stream TTS synthesis using CLI components.
    
    This endpoint processes text using the same logic as the CLI but streams
    results via WebSocket for real-time web interface updates.
    """
    try:
        logger.info(f"Stream TTS request from client #{request.client_id}: text={request.text[:50]}..., voice={request.voice}, language={request.language}, target_language={request.target_language}")
        
        # Send start notification
        await manager.send_json({
            "type": "start",
            "message": "Starting TTS processing..."
        }, request.client_id)
        
        # Process text using unified service (which uses CLI components)
        successful_count = 0
        failed_count = 0
        
        async for audio_file, audio_url, paragraph_text in tts_service.stream_tts_web(
            request.text, request.voice, request.language, request.target_language, request.client_id
        ):
            try:
                # Send audio URL and text to client
                await manager.send_json({
                    "type": "audio_url",
                    "url": audio_url,
                    "text": paragraph_text
                }, request.client_id)
                
                successful_count += 1
                logger.info(f"Streamed audio chunk {successful_count} to client #{request.client_id}")
            
            except Exception as e:
                logger.error(f"Error streaming chunk to client #{request.client_id}: {e}")
                failed_count += 1
        
        # Send completion notification
        completion_message = {
            "type": "complete",
            "successful_count": successful_count,
            "failed_count": failed_count
        }
        
        if failed_count > 0:
            completion_message["warning"] = f"{failed_count} chunk(s) failed to process"
        
        if successful_count == 0:
            completion_message["type"] = "error"
            completion_message["message"] = "No audio files generated"
        
        await manager.send_json(completion_message, request.client_id)
        
        logger.info(f"Stream TTS completed for client #{request.client_id}: {successful_count} successful, {failed_count} failed")
        
        return {"status": "processing_started", "successful_count": successful_count, "failed_count": failed_count}
    
    except Exception as e:
        logger.error(f"Stream TTS error for client #{request.client_id}: {e}")
        
        # Send error notification to client
        try:
            await manager.send_json({
                "type": "error",
                "message": str(e)
            }, request.client_id)
        except:
            pass
        
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts/stop/{client_id}")
async def stop_tts_streaming(client_id: int):
    """
    Stop TTS streaming for a specific client.
    """
    try:
        logger.info(f"Stop request received for client #{client_id}")
        
        # Stop the streaming process
        stopped = tts_service.stop_streaming(client_id)
        
        if stopped:
            # Send stop notification via WebSocket
            await manager.send_json({
                "type": "stopped",
                "message": "TTS streaming stopped by user request"
            }, client_id)
            
            logger.info(f"TTS streaming stopped for client #{client_id}")
            return {"status": "stopped", "client_id": client_id}
        else:
            return {"status": "not_streaming", "client_id": client_id, "message": "Client was not streaming"}
    
    except Exception as e:
        logger.error(f"Error stopping TTS for client #{client_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/convert_pdf_to_text")
async def convert_pdf_to_text(file: UploadFile = File(...)):
    """
    Converts an uploaded PDF file to plain text.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # Read the PDF content
        pdf_content = await file.read()
        
        # Use a temporary file to save the PDF content for PyPDF2
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_content)
            temp_pdf_path = temp_pdf.name

        text_chunks = []
        try:
            reader = PdfReader(temp_pdf_path)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                # Remove links, page numbers, and references using regex
                text = re.sub(r'http\S+|www\.\S+', '', text)  # Remove URLs
                text = re.sub(r'\bPage \d+\b', '', text)  # Remove page numbers
                text = re.sub(r'\bReferences?\b', '', text)  # Remove references
                text_chunks.append(text)
            raw_text = "\n".join(text_chunks)
            # Collapse any run of whitespace (spaces, tabs, newlines) to a single space
            cleaned_text = re.sub(r"\s+", " ", raw_text).strip()
            return {"text": cleaned_text}
        finally:
            os.unlink(temp_pdf_path) # Clean up the temporary PDF file

    except Exception as e:
        logger.error(f"Error converting PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to convert PDF: {str(e)}")

# --- Utility Endpoints ---
@app.post("/api/cleanup")
async def cleanup_old_files(max_age_hours: int = 24):
    """Clean up old audio files."""
    try:
        cleanup_count = await tts_service.cleanup_old_files(max_age_hours)
        return {"message": f"Cleaned up {cleanup_count} old files"}
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Get service statistics."""
    try:
        # Get session info from unified file manager
        session_info = tts_service.unified_file_manager.get_session_info()
        disk_usage = tts_service.unified_file_manager.get_disk_usage()
        
        stats = {
            "active_connections": len(manager.active_connections),
            "output_directory": settings.output_directory,
            "timestamp": datetime.now().isoformat(),
            "session_info": session_info,
            "disk_usage": disk_usage
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Startup/Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    logger.info("Starting Unified TTS Web Server...")
    logger.info("CLI components loaded and ready")
    logger.info("Web interface available at http://localhost:8000")
    logger.info("API documentation at http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Shutting down Unified TTS Web Server...")
    
    # Disconnect all WebSocket clients
    for client_id in list(manager.active_connections.keys()):
        manager.disconnect(client_id)

# --- Main Execution ---
def main():
    """Main function to run the web server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified TTS Web Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    logger.info("This server combines CLI TTS components with web interface")
    logger.info("Use CLI: python -m src.main")
    logger.info("Use Web: http://localhost:8000")
    
    uvicorn.run(
        "src.web_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()