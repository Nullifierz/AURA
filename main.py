from contextlib import asynccontextmanager
import threading
import asyncio
from typing import List
from core.brain import Brain
from core.mouth import Mouth
from core.ears import Ears, ListeningState
from core.logger import AURALogger, get_logger
from core.tools.weather_tool import get_weather, get_weather_data
from settings.config_loader import config
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

log_level = config.get('system.log_level', 'INFO')
AURALogger.setup(log_level=log_level, log_to_file=True)

logger = get_logger(__name__)

logger.info("Starting AURA application")

# --- Global Components ---
brain = Brain()
mouth = Mouth()
ears = Ears()
global_loop = None

# --- Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")

manager = ConnectionManager()

# --- Voice Callbacks ---
def on_wake_word(text: str):
    """Called when wake word is detected"""
    logger.info(f"Wake word detected: {text}")
    # Optional: Play a sound or visual cue here
    # mouth.speak("Yes?") # Uncomment for verbal acknowledgement
    
    # Notify frontend of wake state
    if global_loop:
        asyncio.run_coroutine_threadsafe(
            manager.broadcast({
                "type": "state_change",
                "state": "listening",
                "wake_word": text
            }),
            global_loop
        )

def on_voice_command(text: str):
    """Called when a full voice command is received"""
    logger.info(f"Processing voice command: {text}")
    
    # Notify frontend: Processing
    if global_loop:
        asyncio.run_coroutine_threadsafe(
            manager.broadcast({
                "type": "state_change",
                "state": "processing",
                "query": text
            }),
            global_loop
        )

    try:
        # 1. Send to Brain
        ears.set_state(ListeningState.PROCESSING)
        result = brain.generate(text)
        response_text = result["response"]
        hud_sections = result.get("hud_sections", [])
        
        # 2. Generate Audio (Base64)
        # We use speak() to get the base64 string, NOT say() which plays locally
        b64_audio = mouth.speak(response_text)
        
        # 3. Notify frontend: Result (HUD + Text + Audio)
        if global_loop:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast({
                    "type": "voice_response",
                    "response": response_text,
                    "hud_sections": hud_sections,
                    "base64_audio": b64_audio
                }),
                global_loop
            )
        
        # 4. Handle Playback
        # If we have connected clients, they will play the audio (via WebSocket)
        # If NOT, we play locally as a fallback
        if not manager.active_connections:
            logger.info("No frontend connected, playing audio locally.")
            ears.set_state(ListeningState.SPEAKING)
            mouth.say(response_text) # This re-generates PCM but it's safer/easier
            ears.clear_audio_queue()
        else:
            logger.info("Frontend connected, sent audio for remote playback.")
            # We still set state to SPEAKING so the visualizer (if simulated) or logic knows
            ears.set_state(ListeningState.SPEAKING)
            
            # Wait for approximate duration of speech to avoid picking up echo
            # Estimate: 15 chars per second?
            duration = len(response_text) / 15.0
            import time
            time.sleep(duration)
            ears.clear_audio_queue()
        
        # 5. Return to listening
        ears.set_state(ListeningState.LISTENING)
        
        # Notify frontend: Idle/Listening
        if global_loop:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast({
                    "type": "state_change",
                    "state": "idle"
                }),
                global_loop
            )
        
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        mouth.say("I'm sorry, I encountered an error.")
        ears.set_state(ListeningState.LISTENING)
        
        if global_loop:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast({
                    "type": "error",
                    "message": str(e)
                }),
                global_loop
            )

# Wire up the ears
ears.on_wake_word_callback = on_wake_word
ears.on_command_callback = on_voice_command

# --- FastAPI Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Capture the event loop for thread-safe calls
    global global_loop
    global_loop = asyncio.get_running_loop()
    
    # Startup: Run Ears in a separate thread so it doesn't block FastAPI
    logger.info("Starting Voice Assistant thread...")
    voice_thread = threading.Thread(target=ears.run, daemon=True)
    voice_thread.start()
    
    yield
    
    # Shutdown: Cleanly stop Ears
    logger.info("Stopping Voice Assistant...")
    ears.stop()
    voice_thread.join(timeout=5.0)

app = FastAPI(
    title="Backend AURA API",
    description="API for AURA backend services",
    version="0.0.1",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Currently we don't expect messages from client via WS, but we can log them
            logger.debug(f"Received WS message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

class QueryRequest(BaseModel):
    query: str

@app.post("/generate")
def generate(request: QueryRequest):
    try:
        # Brain now returns both response and HUD sections
        result = brain.generate(request.query)
        
        # Generate audio from text response
        base64_audio = mouth.speak(result["response"])
        
        return {
            "response": result["response"],
            "base64_audio": base64_audio,
            "hud_sections": result.get("hud_sections", [])
        }
    except Exception as e:
        logger.error(f"Error in /generate: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
if __name__ == "__main__":
    # Run the FastAPI server (which starts Ears via lifespan)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)