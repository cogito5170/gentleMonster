"""Chromium, called directly (no Python browser driver needed): print to PDF, and dump the DOM after the page's
own QA script has measured it. Both say plainly when Chromium is missing or fails -- they never fake a file."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from gentle_monster import paths

BASE = ["--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
        "--disable-extensions", "--no-first-run", "--font-render-hinting=none"]


def available() -> "str | None":
    return paths.chromium()


def shell() -> "str | None":
    """chrome-headless-shell: unlike `chrome --headless=new` it honours windows narrower than 500 px
    (measured: --window-size=375,800 gave a 500 px viewport in chrome, 375 px here)."""
    import glob
    import os
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    hits = sorted(glob.glob(f"{base}/chromium_headless_shell-*/chrome-linux/headless_shell"))
    return hits[-1] if hits else None


def _run(args, timeout=180, exe=None):
    exe = exe or available()
    if not exe:
        return None, "Chromium not found (PLAYWRIGHT_BROWSERS_PATH / /opt/pw-browsers)"
    try:
        p = subprocess.run([exe, *BASE, *args], capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, f"Chromium timed out after {timeout} s"
    return p, None


def count_pages(pdf: Path) -> int:
    data = pdf.read_bytes()
    return len(re.findall(rb"/Type\s*/Page(?!s)", data))


def render(html_path, pdf_path) -> dict:
    html_path, pdf_path = Path(html_path).resolve(), Path(pdf_path).resolve()
    if pdf_path.exists():
        pdf_path.unlink()
    p, err = _run([f"--print-to-pdf={pdf_path}", "--no-pdf-header-footer", "--virtual-time-budget=4000",
                   html_path.as_uri()])
    if err:
        return {"ok": False, "error": err}
    if not pdf_path.is_file() or pdf_path.stat().st_size < 1000:
        return {"ok": False, "error": f"no PDF written (exit {p.returncode}): {p.stderr.decode(errors='replace')[-400:]}"}
    return {"ok": True, "path": str(pdf_path), "pages": count_pages(pdf_path), "bytes": pdf_path.stat().st_size}


def measure(html_path, width: int, height: int, mode: str = "qa") -> dict:
    """Load the page at a window size with #qa (or #qa-print) and read back what its script measured."""
    import json
    args = [f"--window-size={width},{height}", "--virtual-time-budget=4000", "--dump-dom", Path(html_path).resolve().as_uri() + "#" + mode]
    sh = shell()
    p, err = _run(["--no-sandbox", *args] if sh else args, timeout=120, exe=sh)
    if err:
        return {"ok": False, "error": err}
    dom = p.stdout.decode("utf-8", errors="replace")
    m = re.search(r'<script type="application/json" id="qa-result">(.*?)</script>', dom, re.S)
    if not m:
        return {"ok": False, "error": "page did not report (QA script missing or did not run)"}
    import html as H
    return {"ok": True, **json.loads(H.unescape(m.group(1)))}
