"""
main.py — JARVIS controller.

Flow:
  1. Double-clap       → JARVIS wakes up
  2. Speak a command   → sent to OpenRouter
  3. LLM reply parsed:
       ACTION: OPEN_APP spotify   → opens Spotify
       ACTION: SEARCH <query>     → Google search
       ACTION: PLAY_YOUTUBE <q>   → YouTube search
       plain text                 → spoken as-is
  4. Stays active (keeps listening) until silence or "goodbye"
  5. Auto-sleeps       → back to waiting for double-clap

Adding features:
  • New app     → add path to APP_PATHS in config.py
  • New action  → add handler in actions.py _HANDLERS dict
"""

import re
import time
import config
import voice
import brain
import actions
import spotify

RETRY_LIMIT   = 3
PAUSE_BETWEEN = 0.3

EXIT_WORDS = {"exit", "quit", "goodbye", "bye", "shut down"}

# ── Local intent rules (checked BEFORE the LLM) ──────────────────
# Faster, more reliable for known commands — LLM only for unknown queries.

_SPOTIFY_TRIGGERS = re.compile(
    r"^(pause|resume|play|stop music|next|skip|previous|back|go back|"
    r"volume up|volume down|louder|quieter|turn up|turn down|"
    r"what.?s playing|current song|now playing|what song|"
    r"play\s+.+)$",
    re.IGNORECASE
)

_OPEN_TRIGGERS = re.compile(
    r"^open\s+(\w+)$", re.IGNORECASE
)

_SEARCH_TRIGGERS = re.compile(
    r"^search(?:\s+for)?\s+(.+)$", re.IGNORECASE
)

_YOUTUBE_TRIGGERS = re.compile(
    r"^(?:play\s+(.+)\s+on\s+youtube|youtube\s+(.+))$", re.IGNORECASE
)


def _local_route(text: str) -> str | None:
    """
    Try to match text locally without calling the LLM.
    Returns a spoken response string, or None to fall through to LLM.
    """
    t = text.strip().lower()

    # YouTube (must check before Spotify "play" catch-all)
    m = _YOUTUBE_TRIGGERS.match(t)
    if m:
        query = m.group(1) or m.group(2)
        return actions._handle_play_youtube(query)

    # Spotify controls + "play X" (non-YouTube)
    if _SPOTIFY_TRIGGERS.match(t):
        return spotify.handle(t)

    # Open app / website
    m = _OPEN_TRIGGERS.match(text.strip())
    if m:
        return actions._handle_open_app(m.group(1))

    # Google search
    m = _SEARCH_TRIGGERS.match(t)
    if m:
        return actions._handle_search(m.group(1))

    return None   # no local match → send to LLM


def startup():
    print("=" * 50)
    print("  J.A.R.V.I.S — AI Desktop Assistant")
    print("=" * 50)
    for w in config.validate():
        print(f"  [!] {w}")
    print()
    voice.speak("JARVIS online. Double-clap to activate.")


def handle(text: str) -> bool:
    """
    Process one user utterance.
    Returns False if JARVIS should shut down.
    """
    t = text.strip().lower()

    # 1. Exit check
    if any(word in t for word in EXIT_WORDS):
        voice.speak("Goodbye. JARVIS going offline.")
        return False

    # 2. Local intent match (fast, no API call)
    response = _local_route(text)

    # 3. Fall through to LLM if no local match
    if response is None:
        reply = brain.ask(text)
        was_action, response = actions.parse_and_execute(reply)

    voice.speak(response)
    return True


def active_session() -> bool:
    """
    Active loop: keep listening and responding until the user goes
    quiet or says goodbye.
    Returns False only if JARVIS should fully shut down.
    """
    voice.speak("Yes, I'm listening.")
    failures = 0

    while True:
        text = voice.listen()

        if not text:
            failures += 1
            if failures >= RETRY_LIMIT:
                voice.speak("Going back to sleep. Double-clap to wake me.")
                return True
            time.sleep(PAUSE_BETWEEN)
            continue

        failures = 0
        keep_running = handle(text)
        if not keep_running:
            return False

        time.sleep(PAUSE_BETWEEN)


def main():
    startup()

    while True:
        try:
            # ── SLEEP ────────────────────────────────────────────
            voice.wait_for_double_clap()

            # ── ACTIVE ───────────────────────────────────────────
            keep_running = active_session()
            if not keep_running:
                break

        except KeyboardInterrupt:
            print("\n[main] Stopped.")
            voice.speak("JARVIS shutting down.")
            break
        except Exception as e:
            print(f"[main] Error: {e}")
            voice.speak("I encountered an error. Going back to sleep.")
            time.sleep(1)


if __name__ == "__main__":
    main()