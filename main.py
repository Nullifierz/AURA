from core.brain import Brain
from core.mouth import Mouth
from core.logger import AURALogger, get_logger
from core.tools.weather_tool import get_weather, get_weather_data
from settings.config_loader import config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

log_level = config.get('system.log_level', 'INFO')
AURALogger.setup(log_level=log_level, log_to_file=True)

logger = get_logger(__name__)

logger.info("Starting AURA application")

app = FastAPI(
    title="Backend AURA API",
    description="API for AURA backend services",
    version="0.0.1"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

brain = Brain()
mouth = Mouth()

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
    uvicorn.run(app, host="0.0.0.0", port=8000)