"""Photoreal stills and the 30-second walkthrough MP4.

Stills: open web.page(mode=eye|cut) in headless Chromium, wait for window.__done, screenshot the canvas.
Video:  _part opens the tour page, calls window.renderAt(k / fps) for every frame and pipes JPEGs
        into ffmpeg (libx264). 30 s is split across worker processes, then joined with ffmpeg concat.
        Measured in a build container (swiftshader, 4 cores): 1.1-2.0 s per frame, 12-18 min per video.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from gentle_monster import paths, web

FPS, DUR = 24, 30.0


def stills(job: dict, out_dir, views=("eye", "cut"), w: int = 1600, h: int = 1000) -> "dict[str, str]":
    from playwright.sync_api import sync_playwright
    out_dir = Path(out_dir)
    res = {}
    with sync_playwright() as p:
        b = paths.launch(p)
        for v in views:
            pg = b.new_page(viewport={"width": w, "height": h})
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(web.write(job, v, out_dir / f"_{v}.html", w=w, h=h).as_uri(), wait_until="commit", timeout=180000)
            pg.wait_for_function("window.__done === true || window.__err", timeout=600000)
            err = pg.evaluate("window.__err") or (errs[0] if errs else None)
            if err:
                raise RuntimeError(f"scene error ({v}): {str(err)[:400]}")
            f = out_dir / f"render_{v}.png"
            pg.locator("canvas").screenshot(path=str(f))
            res[v] = str(f)
            pg.close()
        b.close()
    return res


def _part(job_path: str, t0: float, t1: float, out: str, crf: int) -> None:
    """One slice of the video: frames t0..t1 of the tour page, piped into ffmpeg."""
    import json
    import imageio_ffmpeg
    from playwright.sync_api import sync_playwright
    page = Path(out).with_suffix(".html")
    web.write(json.loads(Path(job_path).read_text(encoding="utf-8")), "tour", page)
    with sync_playwright() as p:
        b = paths.launch(p)
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(page.as_uri(), wait_until="commit", timeout=180000)
        pg.wait_for_function("window.__ready===true", timeout=600000)
        if errs:
            raise RuntimeError("scene error: " + "; ".join(errs[:3]))
        k0, k1 = int(round(t0 * FPS)), int(round(t1 * FPS))
        proc = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
                                 "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(crf), "-preset", "medium", str(out)], stdin=subprocess.PIPE)
        for k in range(k0, k1):
            pg.evaluate(f"window.renderAt({k / FPS})")
            proc.stdin.write(pg.screenshot(type="jpeg", quality=90))
            if k % 60 == 0:
                print(f"[gentle_monster] frame {k}/{k1}", flush=True)
        proc.stdin.close(); proc.wait()
        b.close()


def video(job_path, out_mp4, workers: int = 0, crf: int = 20, seconds: float = DUR) -> str:
    import imageio_ffmpeg
    out_mp4 = Path(out_mp4)
    tmp = out_mp4.parent / ("_parts_" + out_mp4.stem)
    tmp.mkdir(parents=True, exist_ok=True)
    n = workers or max(1, min(4, os.cpu_count() or 1))
    procs = []
    for i in range(n):
        a, b = seconds * i / n, seconds * (i + 1) / n
        procs.append(subprocess.Popen([sys.executable, "-m", "gentle_monster.render", "part", str(job_path), str(a), str(b), str(tmp / f"p{i}.mp4"), str(crf)],
                                      cwd=str(paths.REPO)))
    rc = [p.wait() for p in procs]
    if any(rc):
        raise RuntimeError(f"a video slice failed: exit codes {rc}")
    (tmp / "list.txt").write_text("".join(f"file 'p{i}.mp4'\n" for i in range(n)))
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                    "-c", "copy", "-movflags", "+faststart", str(out_mp4)], check=True)
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    return str(out_mp4)


if __name__ == "__main__":
    if sys.argv[1] == "part":
        _part(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5], int(sys.argv[6]))
