"""
config.py — Central configuration for JARVIS.
Edit APP_PATHS to match your actual install locations.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── OpenRouter ────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL   = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_URL     = "https://openrouter.ai/api/v1/chat/completions"
MAX_TOKENS         = 300
TEMPERATURE        = 0.7

# ── App Paths ─────────────────────────────────────────────────────
# Update these to match your actual installation paths.
APP_PATHS = {
    # Spotify — tries the standard user-install location
    # If yours is different, paste the correct path here
    "spotify":     r"C:\Users\GURUMITHRAN V\OneDrive\Desktop\Spotify.lnk",
    "claude":      r"C:\Users\GURUMITHRAN V\AppData\Local\AnthropicClaude\claude.exe",
    "antigravity": r"E:\Antigravity\Antigravity.exe",
    "notepad":     r"C:\Windows\System32\notepad.exe",
    "calculator":  r"C:\Windows\System32\calc.exe",
    "vscode":      r"C:\Users\GURUMITHRAN V\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "chrome":      r"C:\Program Files\Google\Chrome\Application\chrome.exe",
}

# ── Audio Settings ────────────────────────────────────────────────
SAMPLE_RATE      = 16000
RECORD_SECONDS   = 6
SILENCE_THRESHOLD = 500
SILENCE_DURATION  = 1.5

# ── Clap Detection ────────────────────────────────────────────────
CLAP_THRESHOLD     = 3000   # RMS spike level (0–32768 scale)
CLAP_MIN_GAP       = 0.08   # ignore spikes closer than this (same clap)
DOUBLE_CLAP_WINDOW = 1.2    # second clap must arrive within this window
CLAP_CHUNK         = 0.04   # seconds per analysis chunk

# ── TTS ───────────────────────────────────────────────────────────
EDGE_VOICE = "en-US-GuyNeural"   # Microsoft neural voice

# ── Master System Prompt ──────────────────────────────────────────
SYSTEM_PROMPT = """You are JARVIS, a highly intelligent, fast, and precise AI desktop assistant.

Your role:
- Understand user voice commands
- Respond naturally and briefly
- Detect actionable intents
- Output structured responses when needed

Rules:
1. If the user asks to open an app → return exactly:
   ACTION: OPEN_APP <app_name>

2. If the user asks to search something → return exactly:
   ACTION: SEARCH <query>

3. If the user asks to play music/video → return exactly:
   ACTION: PLAY_YOUTUBE <query>

4. If it's a normal conversation → respond naturally in 1-2 sentences.

5. Keep responses short and assistant-like.

6. Never explain your internal logic.

Examples:
User: open spotify
Output: ACTION: OPEN_APP spotify

User: play arijit singh songs
Output: ACTION: PLAY_YOUTUBE arijit singh songs

User: search python tutorials
Output: ACTION: SEARCH python tutorials

User: how are you
Output: I am functioning perfectly. How can I assist you?"""


# ── Validation ────────────────────────────────────────────────────
def validate():
    warnings = []
    if not OPENROUTER_API_KEY:
        warnings.append("OPENROUTER_API_KEY not set — AI will not work.")
    return warnings