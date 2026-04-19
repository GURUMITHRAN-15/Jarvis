"""
voice.py — Audio I/O for JARVIS.

TTS  : edge-tts (Microsoft neural) + playsound playback (no build needed)
STT  : sounddevice → sr.AudioData → Google Speech API (no PyAudio)
Wake : double-clap detector via RMS spike pattern
"""

import asyncio
import os
import tempfile
import time
import threading
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from playsound import playsound
import edge_tts

import config

# ── TTS ───────────────────────────────────────────────────────────
_tts_lock = threading.Lock()


async def _synthesise(text: str, path: str):
    communicate = edge_tts.Communicate(text, config.EDGE_VOICE)
    await communicate.save(path)


def speak(text: str) -> None:
    """Speak text aloud and block until done."""
    print(f"\n[JARVIS] {text}\n")
    with _tts_lock:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        path = tmp.name
        tmp.close()
        try:
            asyncio.run(_synthesise(text, path))
            playsound(path)          # blocks until audio finishes
        except Exception as e:
            print(f"[voice] TTS error: {e}")
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass


# ── Double-clap wake ──────────────────────────────────────────────
def wait_for_double_clap() -> None:
    """Block until two claps are detected within DOUBLE_CLAP_WINDOW seconds."""
    print("[JARVIS] Sleeping... (double-clap to wake)", flush=True)

    chunk = int(config.SAMPLE_RATE * config.CLAP_CHUNK)
    clap_times: list[float] = []
    last_spike = 0.0

    with sd.InputStream(samplerate=config.SAMPLE_RATE, channels=1,
                        dtype="float32", blocksize=chunk) as stream:
        while True:
            data, _ = stream.read(chunk)
            rms = float(np.sqrt(np.mean(data ** 2))) * 32768
            now = time.time()

            if rms > config.CLAP_THRESHOLD and (now - last_spike) > config.CLAP_MIN_GAP:
                last_spike = now
                clap_times = [t for t in clap_times
                              if now - t < config.DOUBLE_CLAP_WINDOW]
                clap_times.append(now)
                print(f"[voice] Clap {len(clap_times)}/2", flush=True)

                if len(clap_times) >= 2:
                    print("[JARVIS] Awake!")
                    return


# ── STT ───────────────────────────────────────────────────────────
def _record_audio() -> np.ndarray:
    """Record mic until silence after speech, or max RECORD_SECONDS."""
    chunk_size   = int(config.SAMPLE_RATE * 0.1)
    max_chunks   = int(config.RECORD_SECONDS / 0.1)
    silent_limit = int(config.SILENCE_DURATION / 0.1)

    frames, silent_chunks, started = [], 0, False

    try:
        with sd.InputStream(samplerate=config.SAMPLE_RATE, channels=1,
                            dtype="float32", blocksize=chunk_size) as stream:
            for _ in range(max_chunks):
                data, _ = stream.read(chunk_size)
                frames.append(data.copy())
                rms = float(np.sqrt(np.mean(data ** 2))) * 32768

                if rms > config.SILENCE_THRESHOLD:
                    started = True
                    silent_chunks = 0
                elif started:
                    silent_chunks += 1
                    if silent_chunks >= silent_limit:
                        break
    except sd.PortAudioError as e:
        print(f"[voice] Mic error: {e}")
        return np.array([], dtype="float32")

    return np.concatenate(frames) if frames else np.array([], dtype="float32")


def listen() -> str | None:
    """Record one voice command and return recognised text, or None."""
    print("[JARVIS] Listening...")
    audio_np = _record_audio()

    if audio_np.size == 0:
        print("[voice] No audio.")
        return None

    pcm   = (audio_np * 32767).astype(np.int16).tobytes()
    audio = sr.AudioData(pcm, config.SAMPLE_RATE, 2)

    try:
        text = sr.Recognizer().recognize_google(audio)
        print(f"[You] {text}")
        return text.strip()
    except sr.UnknownValueError:
        print("[voice] Could not understand.")
        return None
    except sr.RequestError as e:
        print(f"[voice] STT error: {e}")
        return None