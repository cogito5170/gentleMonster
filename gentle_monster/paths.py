"""Where gentle_monster reads and writes. Outputs never go into tracked files."""
from __future__ import annotations

import os
import re
from pathlib import Path

PKG = Path(__file__).resolve().parent
REPO = PKG.parent
WEB = PKG / "web"
VENDOR = PKG / "vendor"
EXAMPLES = PKG / "examples"
OUT = Path(os.environ.get("GENTLE_MONSTER_OUT") or (REPO / "out"))   # ignored by git
PHOTOS = REPO / "photos"                                              # put your own photos / reference layouts here


def job_dir(name: str) -> Path:
    """One folder per job. The name is reduced to a safe slug so a Discord message cannot walk out of OUT."""
    slug = re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", (name or "job").strip())[:60].strip("_") or "job"
    d = OUT / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def chromium() -> "str | None":
    """A preinstalled Chromium under PLAYWRIGHT_BROWSERS_PATH if there is one; else Playwright's own."""
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    for pat in ("chromium-*/chrome-linux/chrome", "chromium/chrome-linux/chrome"):
        hits = sorted(Path(base).glob(pat))
        if hits:
            return str(hits[-1])
    return None


def launch(pw, gl: bool = True):
    args = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] if gl else []
    exe = chromium()
    return pw.chromium.launch(executable_path=exe, args=args) if exe else pw.chromium.launch(args=args)


def resolve_photo(p: str) -> Path:
    """Photo paths may be written by a bot or a model, so only files inside photos/, the Discord attachment
    inbox, this tool's output folder, or a folder in GENTLE_MONSTER_PHOTO_DIRS (os.pathsep-separated)
    are accepted. Anything else raises ValueError."""
    extra = [Path(d) for d in os.environ.get("GENTLE_MONSTER_PHOTO_DIRS", "").split(os.pathsep) if d]
    allowed = [a.resolve() for a in [PHOTOS, REPO / "inbox" / "discord_attachments", OUT, *extra]]
    q = Path(p)
    q = (q if q.is_absolute() else REPO / q).resolve()
    if not any(q == a or a in q.parents for a in allowed):
        raise ValueError(f"photo path outside the allowed folders: {p}")
    return q
