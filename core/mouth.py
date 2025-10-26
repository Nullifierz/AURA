import subprocess
import wave
import io
from pathlib import Path
import base64
import re

from core.logger import get_logger

logger = get_logger(__name__)

def sanitize_text(text: str) -> str:
        """
        Remove invalid Unicode characters that can cause encoding errors in TTS.
        
        Args:
            text: Input text that may contain invalid characters
            
        Returns:
            str: Cleaned text safe for UTF-8 encoding
        """
        try:          
            # First, handle surrogates by replacing them with empty string
            # Surrogates are in range U+D800 to U+DFFF
            cleaned = ''.join(char for char in text if not (0xD800 <= ord(char) <= 0xDFFF))
            
            # Encode to UTF-8 with error handling to remove any remaining problematic characters
            cleaned = cleaned.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            
            # Remove control characters except common whitespace
            cleaned = ''.join(char for char in cleaned 
                            if char.isprintable() or char in '\n\r\t ')
            
            # Replace forward slashes with "or"
            cleaned = cleaned.replace('/', ' or ')
            
            # Remove asterisks and hyphens
            cleaned = cleaned.replace('*', '').replace('-', '')
            
            # Remove line breaks (newlines) and replace with space
            cleaned = cleaned.replace('\n', ' ').replace('\r', ' ')
            
            # Replace multiple spaces with single space
            cleaned = re.sub(r' {2,}', ' ', cleaned)
            
            # Final validation: try encoding to UTF-8
            test_encode = cleaned.encode('utf-8')
            
            return cleaned.strip()
        except Exception as e:
            logger.warning(f"Error sanitizing text: {e}")
            # Last resort: extract only safe ASCII characters
            
            safe_text = ''.join(char for char in text if 32 <= ord(char) < 127 or char in ' \n\r\t')
            safe_text = re.sub(r' {2,}', ' ', safe_text)
            return safe_text.strip()

class Mouth:
    """Text-to-Speech using Piper for frontend playback"""
    
    def __init__(self, model_name="cori", data_dir="data/models/piper"):
        """
        Initialize Piper TTS.
        
        Args:
            model_name: Name of the voice model (e.g., "cori", "alba")
            data_dir: Directory containing Piper models
        """
        logger.info(f"Initializing Mouth with model: {model_name}")
        self.data_dir = Path(data_dir)
        self.model_name = model_name
        self.model_path = self._find_model(model_name)
        logger.debug(f"Model path: {self.model_path}")
        logger.info("Mouth initialized successfully")
    
    def _find_model(self, model_name):
        """Find the model file based on the model name."""
        logger.debug(f"Searching for model '{model_name}' in {self.data_dir}")
        # Search for model files containing the model name
        model_files = list(self.data_dir.glob(f"*{model_name}*.onnx"))
        
        if not model_files:
            logger.error(f"No model found with name '{model_name}' in {self.data_dir}")
            raise FileNotFoundError(
                f"No model found with name '{model_name}' in {self.data_dir}"
            )
        
        logger.debug(f"Found {len(model_files)} model file(s)")
        
        # Prefer high quality models, then medium, then any
        for quality in ["high", "medium", "low"]:
            for model_file in model_files:
                if quality in model_file.name:
                    logger.debug(f"Selected {quality} quality model: {model_file.name}")
                    return model_file
        
        # Return the first found model
        logger.debug(f"Using first available model: {model_files[0].name}")
        return model_files[0]
    
    def speak(self, text):
        """
        Convert text to speech and return base64 encoded audio for frontend playback.
        
        Args:
            text: The text to convert to speech
            
        Returns:
            Base64 encoded WAV audio string, or None if error
        """
        if not text or text.strip() == "":
            logger.warning("Empty text provided to speak()")
            return None
        
        # Log original text for debugging
        logger.debug(f"Original text: {text[:100]}..." if len(text) > 100 else f"Original text: {text}")
        
        # Sanitize text to remove invalid Unicode characters
        text = sanitize_text(text)
        
        if not text:
            logger.warning("Text became empty after sanitization")
            return None
        
        logger.info(f"Generating speech for text (length: {len(text)})")
        logger.debug(f"Sanitized text: {text[:100]}..." if len(text) > 100 else f"Sanitized text: {text}")
        
        try:
            # Run Piper to generate speech
            logger.debug("Starting Piper subprocess")
            process = subprocess.Popen(
                [
                    "piper",
                    "--model", str(self.model_path),
                    "--output-raw"
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Send sanitized text to Piper
            stdout, stderr = process.communicate(input=text.encode('utf-8'))
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8')
                logger.error(f"Piper error: {error_msg}")
                return None
            
            logger.debug("Audio generated successfully")
            # Convert raw audio to WAV format
            audio_data = self._raw_to_wav(stdout)
            
            # Encode to base64 for frontend
            b64_audio = base64.b64encode(audio_data).decode('utf-8')
            logger.debug(f"Base64 audio generated (size: {len(b64_audio)})")
            
            return b64_audio
        
        except Exception as e:
            logger.error(f"Error in TTS: {e}", exc_info=True)
            return None
    
    def _raw_to_wav(self, raw_data):
        """Convert raw PCM data to WAV format."""
        with io.BytesIO() as wav_io:
            with wave.open(wav_io, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16 bits
                wf.setframerate(22050)  # 22.05 kHz
                wf.writeframes(raw_data)
            return wav_io.getvalue()