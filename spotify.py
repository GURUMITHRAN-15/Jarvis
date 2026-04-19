"""
spotify.py — Spotify control for JARVIS (Free account, no API needed).

Controls:
  - pause / resume       → Space key
  - next track           → Ctrl + Right
  - previous track       → Ctrl + Left
  - volume up            → Ctrl + Up  (x3 = +~10%)
  - volume down          → Ctrl + Down
  - mute                 → Ctrl + Shift + Down (all the way down)
  - search & open        → opens Spotify web search in browser
  - what's playing       → reads Spotify window title (title = song - artist)

How it works:
  - Focuses the Spotify window, sends the keyboard shortcut, refocuses terminal.
  - For search: opens open.spotify.com/search/<query> in browser.
"""

import time
import subprocess
import webbrowser
import urllib.parse
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False   # don't abort on mouse corner
pyautogui.PAUSE    = 0.05


# ── Window focus helper ───────────────────────────────────────────
def _focus_spotify() -> bool:
    """Bring Spotify window to foreground. Returns True if found."""
    wins = gw.getWindowsWithTitle("Spotify")
    if not wins:
        return False
    wins[0].activate()
    time.sleep(0.4)   # give Windows time to actually focus it
    return True


def _hotkey(*keys) -> str | None:
    """Focus Spotify, send hotkey, return None on success or error string."""
    if not _focus_spotify():
        return "Spotify doesn't seem to be open. Please open it first."
    pyautogui.hotkey(*keys)
    time.sleep(0.2)
    return None


# ── Controls ──────────────────────────────────────────────────────
def pause_resume() -> str:
    err = _hotkey("space")
    return err or "Toggled play/pause."


def next_track() -> str:
    err = _hotkey("ctrl", "right")
    return err or "Skipping to next track."


def previous_track() -> str:
    err = _hotkey("ctrl", "left")
    return err or "Going back to previous track."


def volume_up() -> str:
    if not _focus_spotify():
        return "Spotify is not open."
    for _ in range(3):             # 3 presses ≈ +10%
        pyautogui.hotkey("ctrl", "up")
        time.sleep(0.05)
    return "Volume increased."


def volume_down() -> str:
    if not _focus_spotify():
        return "Spotify is not open."
    for _ in range(3):
        pyautogui.hotkey("ctrl", "down")
        time.sleep(0.05)
    return "Volume decreased."


def now_playing() -> str:
    """Read current track from Spotify window title."""
    wins = gw.getWindowsWithTitle("Spotify")
    if not wins:
        return "Spotify is not open."
    title = wins[0].title.strip()
    # Spotify window title format: "Song Name - Artist Name"
    if title == "Spotify" or not title:
        return "Nothing is playing right now."
    return f"Currently playing: {title}."


def search_and_open(query: str) -> str:
    """Open Spotify web search — user clicks play (free tier limitation)."""
    url = f"https://open.spotify.com/search/{urllib.parse.quote(query)}"
    webbrowser.open(url)
    return f"Opened Spotify search for {query}. Tap play to start."


# ── Smart router ──────────────────────────────────────────────────
def handle(query: str) -> str:
    """
    Route a free-text Spotify query to the right function.

    Supported voice commands:
      pause / play / resume
      next / skip
      previous / back
      volume up / louder
      volume down / quieter
      what's playing / current song
      play <song or artist>   → opens Spotify search in browser
    """
    import re
    q = query.strip().lower()

    if q in ("pause", "stop", "stop music"):
        return pause_resume()
    if q in ("play", "resume", "continue"):
        return pause_resume()
    if q in ("next", "skip", "next song", "next track"):
        return next_track()
    if q in ("previous", "back", "prev", "go back", "previous track"):
        return previous_track()
    if q in ("volume up", "louder", "increase volume", "turn up"):
        return volume_up()
    if q in ("volume down", "quieter", "lower", "decrease volume", "turn down"):
        return volume_down()
    if q in ("what's playing", "current song", "now playing",
             "what song is this", "what song", "whats playing"):
        return now_playing()

    # "play X" → search and open
    play_query = re.sub(r"^(play|search|find)\s+", "", q).strip()
    if play_query:
        return search_and_open(play_query)

    return "I didn't understand that Spotify command."


# ── Standalone test ───────────────────────────────────────────────
if __name__ == "__main__":
    print(now_playing())