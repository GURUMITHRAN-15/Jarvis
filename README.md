# J.A.R.V.I.S — AI Voice Desktop Assistant

A voice-controlled AI desktop assistant built with Python that listens for commands via double-clap, processes them through OpenRouter's LLM, and executes actions like opening apps, searching the web, and controlling Spotify.

---

## ✨ Features

- **🎤 Voice Control**: Capture voice commands via microphone with automatic silence detection
- **👏 Double-Clap Wake**: Detect two rapid claps to activate JARVIS (no always-on listening)
- **🧠 AI Brain**: Powered by OpenRouter (supports GPT-4o-mini, Claude, and more)
- **⚡ Action Engine**: Execute structured commands instantly
  - Open apps (Spotify, Claude, VS Code, etc.)
  - Search Google
  - Play YouTube videos
  - Control Spotify (pause, next, volume, what's playing)
- **🗣️ Natural Voice Output**: Microsoft neural TTS (edge-tts) with clear, natural speech
- **💬 Conversation Memory**: Maintains conversation history within a session
- **🔧 Modular Architecture**: Easy to add new commands and features

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/GURUMITHRAN-15/Jarvis.git
cd Jarvis
pip install -r requirements.txt
```

### 2. Get API Keys

**OpenRouter API Key** (free tier available):
- Visit [openrouter.ai/keys](https://openrouter.ai/keys)
- Create a free account
- Generate an API key
- Copy it

### 3. Configure

Create/edit `.env` in the project root:

```env
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxx
```

### 4. Update App Paths (Optional)

Edit `config.py` to match your app installation locations:

```python
APP_PATHS = {
    "spotify":     r"C:\Users\YourName\AppData\Roaming\Spotify\Spotify.exe",
    "claude":      r"C:\Users\YourName\AppData\Local\AnthropicClaude\claude.exe",
    "vscode":      r"C:\Users\YourName\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "chrome":      r"C:\Program Files\Google\Chrome\Application\chrome.exe",
}
```

### 5. Run

```bash
python main.py
```

Output:
```
==================================================
  J.A.R.V.I.S — AI Desktop Assistant
==================================================

[JARVIS] JARVIS online. Double-clap to activate.
[JARVIS] Sleeping... (double-clap to wake)
```

---

## 📖 How to Use

### Wake Up
👏👏 Double-clap near your microphone (within 1-2 seconds).

JARVIS responds: `"Yes, I'm listening."`

### Give Commands

Speak naturally. JARVIS will:
1. **Capture** your voice
2. **Understand** via OpenRouter
3. **Execute** the action or respond conversationally

### Example Commands

| Say | Action |
|-----|--------|
| `pause` | Pauses Spotify |
| `next song` | Skips to next track |
| `volume up` | Increases Spotify volume |
| `what's playing` | Reads current Spotify track |
| `play blinding lights` | Opens Spotify search in browser |
| `open youtube` | Opens YouTube in browser |
| `search python tutorials` | Google search |
| `open claude` | Launches Claude desktop app |
| `tell me a joke` | AI generates a joke |
| `how are you` | Conversational response |
| `goodbye` | Shuts down JARVIS |

---

## 🏗️ Architecture

```
┌─────────────┐
│   voice.py  │  Microphone input + clap detection + TTS output
└──────┬──────┘
       │
       ├─→ listen()           [records mic, detects silence]
       ├─→ speak(text)        [edge-tts + playsound]
       └─→ wait_for_double_clap()  [RMS spike detection]

┌─────────────┐
│   main.py   │  Main controller & session loop
└──────┬──────┘
       │
       ├─→ _local_route()     [regex intent matching - FAST]
       └─→ handle()           [process command]

┌─────────────┐
│  brain.py   │  OpenRouter LLM integration
└──────┬──────┘
       │
       └─→ ask(text)          [send to OpenRouter, keep history]

┌─────────────┐
│ actions.py  │  Execute ACTION directives
└──────┬──────┘
       │
       ├─→ _handle_open_app()     [launch .exe or browser URL]
       ├─→ _handle_search()       [Google search]
       ├─→ _handle_play_youtube() [YouTube search]
       └─→ _handle_spotify()      [Spotify control]

┌─────────────┐
│ spotify.py  │  Spotify control (free tier, keyboard shortcuts)
└──────┬──────┘
       │
       ├─→ pause_resume()     [Space key]
       ├─→ next_track()       [Ctrl+Right]
       ├─→ volume_up/down()   [Ctrl+Up/Down]
       └─→ now_playing()      [read window title]

┌─────────────┐
│ config.py   │  Settings, API keys, app paths, system prompt
└─────────────┘
```

---

## 📋 Project Structure

```
jarvis/
├── main.py              # Entry point, session loop
├── voice.py             # Mic I/O, STT, TTS, clap detection
├── brain.py             # OpenRouter API integration
├── actions.py           # ACTION handler dispatcher
├── spotify.py           # Spotify control (keyboard shortcuts)
├── config.py            # Settings, API keys, app paths
├── .env                 # Your API keys (NEVER commit this)
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## 🔧 Configuration

### System Prompt (config.py)

The master prompt that controls JARVIS's behavior:

```python
SYSTEM_PROMPT = """You are JARVIS, a highly intelligent, fast, and precise AI desktop assistant.
...
Rules:
1. If user asks to open an app → ACTION: OPEN_APP <app_name>
2. If user asks to search → ACTION: SEARCH <query>
3. If user asks to play music → ACTION: PLAY_YOUTUBE <query>
4. If user asks to control Spotify → ACTION: SPOTIFY_PLAY <query>
...
"""
```

### Audio Settings (config.py)

```python
SAMPLE_RATE      = 16000    # Hz
RECORD_SECONDS   = 6        # max listen window
SILENCE_THRESHOLD = 500     # RMS below = silence
SILENCE_DURATION = 1.5      # seconds of silence to stop recording

# Clap detection
CLAP_THRESHOLD     = 3000   # RMS level (0-32768 scale)
CLAP_MIN_GAP       = 0.08   # seconds (prevent same-clap double-count)
DOUBLE_CLAP_WINDOW = 1.2    # seconds (two claps must arrive within this)
```

---

## 🎤 Local Intent Matching

Before calling the LLM, JARVIS checks a **local regex table** in `main.py`:

```python
_SPOTIFY_TRIGGERS = re.compile(
    r"^(pause|resume|play|next|skip|volume up|what.?s playing|...)$"
)
_OPEN_TRIGGERS = re.compile(r"^open\s+(\w+)$")
_SEARCH_TRIGGERS = re.compile(r"^search(?:\s+for)?\s+(.+)$")
```

**Why?** Faster response, no API latency for known commands.

---

## 🛠️ Troubleshooting

### Microphone not detected
```powershell
# List all audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Set as default in Windows Settings → Sound → Advanced
```

### Speech not recognized
- Speak clearly and pause before starting
- Check internet (Google STT is online)
- Increase `SILENCE_THRESHOLD` if background noise is high

### Spotify shortcuts not working
- Spotify must be installed and accessible
- Spotify window doesn't need focus (JARVIS focuses it automatically)
- Free tier limitations: no search/play, only pause/next/volume

### "No audio captured" error
- Check microphone volume in Windows
- Try a different USB mic
- Increase `RECORD_SECONDS` in config.py

### OpenRouter API errors
- Verify API key is correct in `.env`
- Check rate limits (free tier: ~5 req/min)
- Try a different model: `OPENROUTER_MODEL=anthropic/claude-3-haiku`

---

## 🚀 Adding New Features

### Add a new app to launcher
Edit `config.py`:

```python
APP_PATHS = {
    "notion": r"C:\Users\...\Notion.exe",
    ...
}
```

Done. Users can now say: *"open notion"*

### Add a new command handler
Edit `actions.py`:

```python
def _handle_my_action(value: str) -> str:
    # your code
    return "Done!"

_HANDLERS = {
    "MY_ACTION": _handle_my_action,
    ...
}
```

Update `config.py` system prompt to explain the new action.

### Add a new app/website shortcut
Edit `actions.py`:

```python
_BROWSER_APPS = {
    "twitter": "https://www.twitter.com",
    ...
}
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `sounddevice` | ≥0.4.6 | Microphone recording |
| `numpy` | ≥1.24.0 | Audio processing |
| `SpeechRecognition` | ≥3.10.0 | Google STT |
| `edge-tts` | ≥6.1.9 | Microsoft neural TTS |
| `playsound` | 1.2.2 | Audio playback |
| `python-dotenv` | ≥1.0.0 | Load .env |
| `pyautogui` | ≥0.9.54 | Keyboard shortcuts (Spotify) |
| `pygetwindow` | ≥0.0.9 | Window focus (Spotify) |

---

## 🔐 Security

- ✅ API keys stored in `.env` (never committed)
- ✅ No sensitive data logged to console
- ✅ Conversation history stays local (in-memory)
- ✅ No data sent to Anthropic, only to OpenRouter & Google STT

### Best Practices

1. **Never share your `.env` file**
2. **Rotate API keys if exposed** (even once)
3. **Keep `git log` clean** (use `git filter-repo` if secrets leak)
4. **Review `.gitignore`** before each commit

---

## 📈 Future Enhancements

- [ ] Wake word detection ("Hey Jarvis")
- [ ] GUI dashboard (React/Tkinter)
- [ ] Memory persistence (JSON/DB)
- [ ] WhatsApp automation
- [ ] Screen awareness
- [ ] Multi-language support
- [ ] RAG (chat with your documents)
- [ ] Custom hotkeys

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📝 License

This project is open source. Use and modify freely.

---

## 👨‍💻 Author

**Gurumithran V**
- GitHub: [@GURUMITHRAN-15](https://github.com/GURUMITHRAN-15)
- LinkedIn: [Gurumithran](https://linkedin.com/in/gurumithran-v-b30b99357)

---

## ❓ FAQ

**Q: Can JARVIS run on Mac/Linux?**  
A: Mostly, but Windows-specific parts (Spotify keyboard shortcuts, some app paths) need adjustment. STT, TTS, and LLM work on all platforms.

**Q: Do I need Spotify Premium?**  
A: No. Free tier works with keyboard shortcuts (pause, next, volume). Search/play specific song opens Spotify web search.

**Q: Is my data private?**  
A: Yes. Conversation history stays local. Only speech text and LLM queries go to OpenRouter and Google (for STT).

**Q: Can I use a different LLM?**  
A: Yes. OpenRouter supports 100+ models. Change `OPENROUTER_MODEL` in `.env`:
```env
OPENROUTER_MODEL=anthropic/claude-3-haiku
```

**Q: How accurate is voice recognition?**  
A: ~85-90% with clear speech, no background noise. Google STT is excellent but requires internet.

---

**Happy automating! 🚀**
