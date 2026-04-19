"""
brain.py — OpenRouter LLM integration for JARVIS.

Sends user text to OpenRouter and returns the raw response.
The response may be a natural reply OR a structured ACTION string.
main.py parses which it is.
"""

import json
import urllib.request
import urllib.error

import config

_history: list[dict] = []
MAX_HISTORY = 10


def _trim():
    global _history
    if len(_history) > MAX_HISTORY * 2:
        _history = _history[-(MAX_HISTORY * 2):]


def ask(user_text: str) -> str:
    """
    Send user_text to OpenRouter. Returns the model's raw reply string.
    On error, returns a short error message.
    """
    if not config.OPENROUTER_API_KEY:
        return "OpenRouter API key is not configured. Please update your .env file."

    _history.append({"role": "user", "content": user_text})
    _trim()

    payload = json.dumps({
        "model":       config.OPENROUTER_MODEL,
        "max_tokens":  config.MAX_TOKENS,
        "temperature": config.TEMPERATURE,
        "messages": [
            {"role": "system", "content": config.SYSTEM_PROMPT},
            *_history,
        ],
    }).encode()

    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "HTTP-Referer":  "https://jarvis-local",
        "X-Title":       "JARVIS",
    }

    try:
        req = urllib.request.Request(
            config.OPENROUTER_URL,
            data=payload,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode())

        reply = data["choices"][0]["message"]["content"].strip()
        _history.append({"role": "assistant", "content": reply})
        return reply

    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[brain] HTTP {e.code}: {body}")
        if e.code == 429:
            return "I am being rate-limited. Please wait a moment."
        if e.code == 401:
            return "API key rejected. Please check your .env file."
        return f"API error {e.code}. Please try again."

    except urllib.error.URLError as e:
        print(f"[brain] Network error: {e}")
        return "No internet connection. Cannot reach OpenRouter."

    except Exception as e:
        print(f"[brain] Unexpected error: {e}")
        return "Something went wrong. Please try again."


def clear():
    global _history
    _history = []