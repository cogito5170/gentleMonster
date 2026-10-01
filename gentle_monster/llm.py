"""Gemini, called directly over HTTPS. No SDK, no other model.

    ask(prompt)                          -> text
    ask(prompt, images=[(mime, bytes)])  -> text (vision: the reference-layout read)

Key: GEMINI_API_KEY (or GOOGLE_API_KEY). Model: GEMINI_MODEL, default gemini-2.5-flash.
With no key every caller gets RuntimeError -- the synopsis step then says it cannot run, and the
moodboard keeps its measured style without the vision read. We never substitute another model.
"""
from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def key() -> str:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""


def ask(prompt: str, images=(), model: str = "", timeout: float = 120, retries: int = 2) -> str:
    k = key()
    if not k:
        raise RuntimeError("no Gemini key (set GEMINI_API_KEY)")
    parts = [{"text": prompt}] + [{"inline_data": {"mime_type": m, "data": base64.b64encode(b).decode()}} for m, b in images]
    body = json.dumps({"contents": [{"role": "user", "parts": parts}],
                       "generationConfig": {"temperature": 0.9, "maxOutputTokens": 8192}}).encode()
    url = API.format(model=model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"))
    last = None
    for i in range(retries + 1):
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "x-goog-api-key": k})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read().decode())
            return "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"])
        except urllib.error.HTTPError as e:                  # 429 / 5xx are worth one more try
            last = e
            if e.code not in (429, 500, 502, 503, 504):
                break
        except (urllib.error.URLError, TimeoutError, KeyError, IndexError) as e:
            last = e
        time.sleep(2 * (i + 1))
    raise RuntimeError(f"Gemini call failed: {type(last).__name__}: {last}")
