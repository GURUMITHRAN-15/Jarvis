"""
actions.py — Action execution engine for JARVIS.

Parses LLM responses for ACTION: directives and executes them.
Returns a spoken confirmation string.

To add a new app:  add it to config.APP_PATHS in config.py.
To add a new action: add a handler below and register it in _HANDLERS.
"""

import os
import subprocess
import webbrowser
import urllib.parse

import config


# ── App launcher ──────────────────────────────────────────────────
def _launch_app(name: str) -> str:
    name = name.strip().lower()

    if name not in config.APP_PATHS:
        return f"I don't have {name} in my app list. You can add it in config.py."

    # Fully expand %USERNAME%, %APPDATA%, ~ etc.
    path = os.path.expandvars(os.path.expanduser(config.APP_PATHS[name]))
    print(f"[actions] Resolved path: {path}")

    if not os.path.exists(path):
        return (f"I couldn't find {name}. Resolved to: {path} — "
                f"please update APP_PATHS in config.py.")

    try:
        subprocess.Popen(f'"{path}"', shell=True)
        return f"Opening {name}."
    except Exception as e:
        return f"Failed to open {name}. {e}"


# ── Action handlers ───────────────────────────────────────────────

# Browser-based shortcuts — no exe path needed
_BROWSER_APPS = {
    "youtube":  "https://www.youtube.com",
    "yt":       "https://www.youtube.com",
    "google":   "https://www.google.com",
    "gmail":    "https://mail.google.com",
    "github":   "https://www.github.com",
    "whatsapp": "https://web.whatsapp.com",
    "twitter":  "https://www.twitter.com",
    "linkedin": "https://www.linkedin.com",
}

def _handle_open_app(value: str) -> str:
    key = value.strip().lower()
    if key in _BROWSER_APPS:
        webbrowser.open(_BROWSER_APPS[key])
        return f"Opening {key}."
    return _launch_app(value)


def _handle_search(value: str) -> str:
    query = value.strip()
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    webbrowser.open(url)
    return f"Searching for {query}."


def _handle_play_youtube(value: str) -> str:
    query = value.strip()
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    webbrowser.open(url)
    return f"Playing {query} on YouTube."


_HANDLERS = {
    "OPEN_APP":      _handle_open_app,
    "SEARCH":        _handle_search,
    "PLAY_YOUTUBE":  _handle_play_youtube,
}


# ── Public interface ──────────────────────────────────────────────
def parse_and_execute(llm_response: str) -> tuple[bool, str]:
    """
    Check if llm_response contains an ACTION directive.

    Returns:
        (True,  spoken_confirmation)  — if an action was found and executed
        (False, original_response)    — if it's a plain conversational reply
    """
    line = llm_response.strip()

    # Match: ACTION: VERB rest-of-line
    if line.upper().startswith("ACTION:"):
        parts = line[7:].strip().split(None, 1)   # split into [VERB, value]
        verb  = parts[0].upper() if parts else ""
        value = parts[1] if len(parts) > 1 else ""

        handler = _HANDLERS.get(verb)
        if handler:
            result = handler(value)
            return True, result
        else:
            return True, f"I don't know how to handle the action: {verb}."

    return False, llm_response