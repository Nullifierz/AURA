import sounddevice as sd
import numpy as np
import queue
import threading
from faster_whisper import WhisperModel

# Settings
samplerate = 16000
block_duration = 0.5
chunk_duration = 2
channels = 1

frames_per_block = int(samplerate * block_duration)
frames_per_chunk = int(samplerate * chunk_duration)

audio_queue = queue.Queue()
audio_buffer = []

model_size = "medium.en"

model = WhisperModel(model_size, device="cuda", compute_type="float16")

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

def recorder():
    with sd.InputStream(samplerate=samplerate, channels=channels, blocksize=frames_per_block, callback=audio_callback):
        print("Listening...")
        while True:
            sd.sleep(500)

def transcriber():
    global audio_buffer
    while True:
        block = audio_queue.get()
        audio_buffer.append(block)

        total_frames = sum(len(b) for b in audio_buffer)
        if total_frames >= frames_per_chunk:
            audio_data = np.concatenate(audio_buffer)[:frames_per_chunk]
            audio_buffer = []

            audio_data = audio_data.flatten().astype(np.float32)

            segments, _ = model.transcribe(
                audio_data,
                language="en",
                beam_size=1)
            
            for segment in segments:
                if segment.text.strip():
                    print(f"[{segment.start:.2f} - {segment.end:.2f}]: {segment.text.lower()}")
                    if segment.text.lower() == "jarvis" or segment.text.lower() == "jarvis.":
                        print("Activation word detected!")

threading.Thread(target=recorder, daemon=True).start()
transcriber()