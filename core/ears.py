import queue
import threading
import time
from enum import Enum
from typing import Callable, Optional, List

import numpy as np
import sounddevice as sd
import webrtcvad
from faster_whisper import WhisperModel
from Levenshtein import distance as levenshtein_distance

from settings.config_loader import config
from core.logger import get_logger


logger = get_logger(__name__)


class ListeningState(Enum):
    STANDBY = "standby"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


class Ears:
    """
    Minimal voice input system for AURA.

    - Uses sounddevice + faster-whisper to transcribe short chunks.
    - Detects wake word (e.g. "jarvis") using fuzzy matching.
    - Logs transcripts and wake events.
    - Provides callback hooks you can later wire into Brain/main.py.
    """

    def __init__(self) -> None:
        # Load config
        self._load_config()

        # State & callbacks
        self._state: ListeningState = ListeningState.STANDBY
        self.on_state_change_callback: Optional[Callable[[ListeningState, ListeningState], None]] = None
        self.on_wake_word_callback: Optional[Callable[[str], None]] = None
        self.on_command_callback: Optional[Callable[[str], None]] = None
        self.on_mute_callback: Optional[Callable[[str], None]] = None

        # Audio / transcription
        self._samplerate = 16_000
        self._block_duration = 0.03  # 30ms for VAD compatibility
        self._channels = 1

        self._frames_per_block = int(self._samplerate * self._block_duration)

        self._audio_queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stop_event = threading.Event()
        self._audio_thread: Optional[threading.Thread] = None

        # VAD (Voice Activity Detection) - Mode 3 is most aggressive
        self._vad = webrtcvad.Vad(3)

        # Utterance segmentation (all in milliseconds)
        self.min_speech_ms = 250        # ignore tiny blips
        self.end_of_utterance_ms = 800  # pause length that ends an utterance
        self.max_utterance_ms = 15000   # safety cap

        # Hallucination filters
        self.hallucination_phrases = [
            "thank you", "thanks", "you", "bye", "goodbye", 
            "copyright", "caption", "subtitles"
        ]

        # Load Whisper model
        self._init_model()

    # -------------------------------------------------------------------------
    # Config
    # -------------------------------------------------------------------------

    def _load_config(self) -> None:
        # Wake word
        ww_cfg = config.get("wake_word", {}) or {}
        self.wake_enabled: bool = ww_cfg.get("enabled", True)
        self.wake_primary_words: List[str] = [w.lower() for w in ww_cfg.get("primary_words", ["jarvis"])]
        self.wake_variations: List[str] = [w.lower() for w in ww_cfg.get("acceptable_variations", [])]
        self.similarity_threshold: float = float(ww_cfg.get("similarity_threshold", 0.65))

        self.mute_phrases: List[str] = [p.lower() for p in ww_cfg.get("mute_phrases", [])]
        self.auto_mute_timeout: int = int(ww_cfg.get("auto_mute_timeout", 30))

        # Whisper
        wh_cfg = config.get("whisper", {}) or {}
        self.model_size: str = wh_cfg.get("model_size", "small.en")
        self.device: str = wh_cfg.get("device", "cpu")
        self.compute_type: str = wh_cfg.get("compute_type", "int8")

        logger.info(
            "Ears config loaded | wake_primary=%s, variations=%s, threshold=%.2f, model=%s",
            self.wake_primary_words,
            self.wake_variations,
            self.similarity_threshold,
            self.model_size,
            self.device
        )

    def _init_model(self) -> None:
        logger.info(
            "Loading faster-whisper model: %s on %s (compute_type=%s)",
            self.model_size,
            self.device,
            self.compute_type,
        )
        self._model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        logger.info("Whisper model loaded successfully")

    # -------------------------------------------------------------------------
    # State helpers (used by tests and by integration)
    # -------------------------------------------------------------------------

    def get_state(self) -> str:
        return self._state.value

    def set_state(self, new_state: ListeningState) -> None:
        old = self._state
        if old is new_state:
            return
        self._state = new_state
        logger.info("State changed: %s → %s", old.value, new_state.value)
        if self.on_state_change_callback:
            try:
                self.on_state_change_callback(old, new_state)
            except Exception as e:
                logger.warning("Error in state change callback: %s", e)

    # -------------------------------------------------------------------------
    # Audio capture & transcription
    # -------------------------------------------------------------------------

    def _audio_callback(self, indata, frames, time_info, status) -> None:
        if status:
            logger.debug("Audio status: %s", status)
        # Copy into queue as float32
        self._audio_queue.put(indata.copy())

    def _transcriber_loop(self) -> None:
        logger.info("Audio processing loop started")
        self.set_state(ListeningState.STANDBY)

        last_activity = time.time()
        block_ms = int(self._block_duration * 1000)

        # Utterance tracking
        in_speech = False
        speech_blocks: List[np.ndarray] = []
        speech_ms = 0
        silence_ms = 0

        try:
            while not self._stop_event.is_set():
                try:
                    block = self._audio_queue.get(timeout=0.5)
                except queue.Empty:
                    # Auto-mute if we've been in LISTENING too long with no activity
                    if (
                        self._state == ListeningState.LISTENING
                        and self.auto_mute_timeout > 0
                        and (time.time() - last_activity) > self.auto_mute_timeout
                    ):
                        logger.info("⏱️ Auto-mute timeout (%ds) - returning to standby", self.auto_mute_timeout)
                        self.set_state(ListeningState.STANDBY)
                        if self.on_mute_callback:
                            try:
                                self.on_mute_callback("auto_timeout")
                            except Exception as e:
                                logger.warning("Error in mute callback: %s", e)
                    continue

                # Flatten & ensure float32
                audio_block = block.astype(np.float32).flatten()

                # VAD Check
                # Convert float32 (-1.0 to 1.0) to int16 (-32768 to 32767) for webrtcvad
                audio_int16 = (audio_block * 32767).astype(np.int16).tobytes()
                
                try:
                    is_speech_block = self._vad.is_speech(audio_int16, self._samplerate)
                except Exception as e:
                    # Fallback if VAD fails (e.g. wrong frame size)
                    is_speech_block = False

                if is_speech_block:
                    # We have speech in this block
                    speech_blocks.append(audio_block)
                    speech_ms += block_ms
                    silence_ms = 0
                    in_speech = True
                    last_activity = time.time()

                    # Safety: if utterance is extremely long, force finalize it
                    if speech_ms >= self.max_utterance_ms:
                        logger.debug("Max utterance duration reached (%.1fs), finalizing", speech_ms / 1000)
                        self._finalize_utterance(speech_blocks, speech_ms)
                        # Reset
                        speech_blocks = []
                        speech_ms = 0
                        silence_ms = 0
                        in_speech = False

                    continue

                # This block is silence
                if not in_speech:
                    continue

                # We *were* in speech, now silence
                silence_ms += block_ms
                
                # Keep appending silence to speech_blocks to capture trailing audio
                # but don't let it grow indefinitely (max 500ms trailing silence)
                if silence_ms < 500: 
                    speech_blocks.append(audio_block)

                # If pause long enough, finalize utterance
                if silence_ms >= self.end_of_utterance_ms:
                    if speech_ms >= self.min_speech_ms:
                        logger.debug(
                            "End of utterance detected | speech_ms=%d, silence_ms=%d",
                            speech_ms,
                            silence_ms,
                        )
                        self._finalize_utterance(speech_blocks, speech_ms)
                    else:
                        logger.debug("Ignored short noise (%dms)", speech_ms)

                    # Reset utterance state
                    speech_blocks = []
                    speech_ms = 0
                    silence_ms = 0
                    in_speech = False

        finally:
            logger.info("Audio processing loop stopped")
    
    def _finalize_utterance(self, speech_blocks: List[np.ndarray], speech_ms: int) -> None:
        """
        Concatenate speech blocks, run Whisper once, and handle wake / command / mute logic.
        """
        if not speech_blocks:
            return

        audio = np.concatenate(speech_blocks)
        logger.debug("Transcribing utterance of %.2fs", speech_ms / 1000)

        # Transcribe
        # beam_size=5 gives better accuracy than 1
        segments, info = self._model.transcribe(
            audio, 
            language="en", 
            beam_size=5,
            vad_filter=True, # Use Whisper's internal VAD as a second check
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        text_parts = []
        for seg in segments:
            text = seg.text.strip()
            
            # --- HALLUCINATION FILTER ---
            # 1. Check no_speech_prob (if high, it's likely noise)
            if seg.no_speech_prob > 0.6:
                logger.debug("Ignored segment (high no_speech_prob: %.2f): '%s'", seg.no_speech_prob, text)
                continue
                
            # 2. Check for common Whisper hallucinations on silence
            clean_text = text.lower().strip('.!,?')
            if clean_text in self.hallucination_phrases:
                # Only ignore if confidence is also somewhat low or it's very short
                if seg.avg_logprob < -0.4: # logprob is negative, closer to 0 is better
                    logger.debug("Ignored hallucination phrase: '%s' (score: %.2f)", text, seg.avg_logprob)
                    continue

            if text:
                text_parts.append(text)

        if not text_parts:
            return

        full_text = " ".join(text_parts).strip()
        if not full_text:
            return

        logger.info("🎤 Heard: '%s' (State: %s)", full_text, self._state.value)

        # Wake / mute / command logic
        if self._state == ListeningState.STANDBY:
            if self._fuzzy_match_wake_word(full_text):
                self.set_state(ListeningState.LISTENING)
                if self.on_wake_word_callback:
                    try:
                        self.on_wake_word_callback(full_text)
                    except Exception as e:
                        logger.warning("Error in wake callback: %s", e)
            else:
                logger.debug("🎤 Heard (standby, ignored): '%s'", full_text)

        elif self._state == ListeningState.LISTENING:
            # Check for mute first
            if self._check_mute_phrase(full_text):
                self.set_state(ListeningState.STANDBY)
                if self.on_mute_callback:
                    try:
                        self.on_mute_callback(full_text)
                    except Exception as e:
                        logger.warning("Error in mute callback: %s", e)
                return

            # Treat as one full command
            if self.on_command_callback:
                try:
                    self.on_command_callback(full_text)
                except Exception as e:
                    logger.warning("Error in command callback: %s", e)
            else:
                logger.info("💬 Command (not yet wired to Brain): %s", full_text)

    # -------------------------------------------------------------------------
    # Public run/stop
    # -------------------------------------------------------------------------

    def run(self) -> None:
        """
        Start capturing microphone audio and processing wake word + commands.
        Blocks until interrupted (Ctrl+C).
        """
        if self._audio_thread and self._audio_thread.is_alive():
            logger.warning("Ears already running")
            return

        self._stop_event.clear()

        # Start processing thread
        self._audio_thread = threading.Thread(target=self._transcriber_loop, daemon=True)
        self._audio_thread.start()

        logger.info("🎧 Starting voice input system...")
        logger.info("💡 Say one of these to wake: %s", ", ".join(self.wake_primary_words))

        # Start sounddevice stream in main thread (so Ctrl+C works)
        with sd.InputStream(
            samplerate=self._samplerate,
            channels=self._channels,
            blocksize=self._frames_per_block,
            dtype="float32",
            callback=self._audio_callback,
        ):
            try:
                while not self._stop_event.is_set():
                    time.sleep(0.1)
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received, stopping ears...")
                self.stop()

    def stop(self) -> None:
        self._stop_event.set()
        if self._audio_thread and self._audio_thread.is_alive():
            self._audio_thread.join(timeout=2.0)

    def clear_audio_queue(self) -> None:
        """Clear the audio queue to discard buffered audio (e.g. after speaking)."""
        with self._audio_queue.mutex:
            self._audio_queue.queue.clear()
        logger.debug("Audio queue cleared")

    # -------------------------------------------------------------------------
    # Wake word & mute detection (text-level)
    # -------------------------------------------------------------------------

    @staticmethod
    def _normalize_text(text: str) -> List[str]:
        import re

        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text.split()

    def _fuzzy_match_wake_word(self, text: str) -> bool:
        """
        Return True if any word in `text` is considered a wake word.
        Matches primary_words and acceptable_variations with Levenshtein distance.
        """
        if not self.wake_enabled:
            return False

        words = self._normalize_text(text)
        if not words:
            return False

        primary = self.wake_primary_words
        variations = set(self.wake_variations)

        for word in words:
            # Exact match
            if word in primary or word in variations:
                logger.info("✅ Wake word detected (exact/variation): '%s'", word)
                return True

            # Fuzzy against primary
            for target in primary:
                max_distance = int(round(len(target) * (1 - self.similarity_threshold)))
                dist = levenshtein_distance(word, target)
                if dist <= max_distance:
                    logger.info(
                        "✅ Wake word detected (fuzzy): '%s' matches '%s' (distance=%d, max=%d)",
                        word,
                        target,
                        dist,
                        max_distance,
                    )
                    return True

        return False

    def _check_mute_phrase(self, text: str) -> bool:
        """
        Return True if `text` contains any configured mute phrase.
        """
        if not self.mute_phrases:
            return False
        lowered = text.lower()
        for phrase in self.mute_phrases:
            if phrase and phrase in lowered:
                logger.info("🔇 Mute phrase detected: '%s'", phrase)
                return True
        return False

if __name__ == "__main__":
    ears = Ears()
    # Example: print callbacks; later you can wire these to Brain/main.py
    ears.on_wake_word_callback = lambda text: logger.info("Wake callback: %s", text)
    ears.on_command_callback = lambda text: logger.info("Command callback: %s", text)
    ears.on_mute_callback = lambda text: logger.info("Mute callback: %s", text)

    ears.run()