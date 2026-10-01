"""Genome -> design tokens. The genome is the page's design DNA (a few bounded genes); the tokens are
what CSS reads. Both are deterministic: the same job and genome always give the same page.

Where each token comes from -- nothing is a house style pasted onto every brand:

    colour   the job's palette + accent, re-weighted by room.light (dark_gallery -> a dark page),
             then pushed by `color.ensure` until text meets WCAG contrast (ink >= 7, sub/accent >= 4.5)
    type     a modular scale (gene `ratio`), fluid between 375 px and 1440 px viewports
             (min = 16 px x a flattened ratio, max = 19 px x the full ratio)
    space    an 8 px unit x gene `air`
    motion   gene `motion`: still (nothing moves) | breath (scroll reveal + the threshold breathes)
             | drift (+ floating shards). Always off under prefers-reduced-motion
    matter   the job's four material presets (procedural canvases, documents._TEX_JS)

`dtcg()` exports the same tokens in the W3C Design Tokens Community Group shape ($type / $value),
so a designer can carry them into another tool.
"""
from __future__ import annotations

import hashlib
import json

from gentle_monster.engine import color as C

GENES = {                                        # gene -> allowed values, in order (operators step along them)
    "ratio": (1.2, 1.25, 1.333, 1.414, 1.5, 1.618),
    "air": (0.8, 1.0, 1.25, 1.5, 1.8),
    "cols": (6, 8, 12),
    "tension": (0, 1, 2),                        # how far the reading column sits off-axis, in grid columns
    "mast": ("stencil", "solid", "outline", "split"),
    "voice": ("grotesk", "serif"),
    "motion": ("still", "breath", "drift"),
    "order": ("walk-first", "matter-first", "intent-first"),
}
GROTESK = '"Archivo","Helvetica Neue",Arial,"Liberation Sans",sans-serif'
SERIF = '"Nanum Myeongjo",Georgia,"Liberation Serif","Times New Roman",serif'
MONO = '"JetBrains Mono","DejaVu Sans Mono",Menlo,Consolas,monospace'
VW0, VW1 = 375, 1440                              # fluid type runs between these viewport widths


def seed(job: dict) -> int:
    return int(hashlib.sha1(json.dumps([job.get("brand"), job.get("title")], ensure_ascii=False).encode()).hexdigest()[:8], 16)


def theme(job: dict) -> str:
    return {"dark_gallery": "dark", "white_gallery": "light", "daylight": "light", "warm_spot": "warm"}.get(job.get("room", {}).get("light"), "light")


def genome0(job: dict) -> dict:
    """The first genome, read from the job -- a starting point, not a verdict. The policy may move it."""
    th = theme(job)
    return {"ratio": 1.414 if th == "dark" else 1.333, "air": 1.25, "cols": 12, "tension": 1,
            "mast": "stencil" if th == "dark" else "solid", "voice": "serif" if th == "warm" else "grotesk",
            "motion": "breath", "order": "walk-first"}


def valid(g: dict) -> bool:
    return set(g) == set(GENES) and all(g[k] in GENES[k] for k in GENES)


def _colours(job: dict, th: str) -> dict:
    pal = [p["hex"] for p in job["palette"]]
    by = sorted(pal, key=C.luminance)
    dark, light = by[0], by[-1]
    if th == "dark":
        bg = C.mix(dark, "#000000", .45)
        ink = C.ensure(C.mix(light, "#ffffff", .7), bg, 7)
    else:
        bg = C.mix(light, "#ffffff", .62)
        if th == "warm":
            bg = C.mix(bg, by[len(by) // 2], .1)
        ink = C.ensure(C.mix(dark, "#000000", .55), bg, 7)
    sub = C.ensure(C.mix(ink, bg, .38), bg, 4.5)
    acc = job["accent"]
    acc_text = C.ensure(acc, bg, 4.5)
    on_acc = max(("#ffffff", "#000000"), key=lambda c: C.contrast(c, acc))
    return {"bg": bg, "surface": C.mix(bg, ink, .06), "ink": ink, "sub": sub, "line": C.mix(ink, bg, .72),
            "accent": acc, "accent-text": acc_text, "on-accent": on_acc, "plan-solid": C.mix(bg, ink, .22),
            "plan-zone": C.mix(bg, ink, .12)}


def _fluid(n: float, ratio: float) -> "tuple[float, float, str]":
    """Step n of the scale as clamp(min, a + b vw, max)."""
    r0 = 1 + (ratio - 1) * .7
    lo, hi = 16 * r0 ** n, 19 * ratio ** n
    if hi < lo:
        lo, hi = hi, lo
    slope = (hi - lo) / (VW1 - VW0) * 100
    icpt = lo - slope * VW0 / 100
    return round(lo, 2), round(hi, 2), f"clamp({lo / 16:.4f}rem, {icpt / 16:.4f}rem + {slope:.4f}vw, {hi / 16:.4f}rem)"


def tokens(job: dict, g: dict) -> dict:
    assert valid(g), f"genome out of range: {g}"
    th = theme(job)
    col = _colours(job, th)
    steps = {(f"step-m{-n}" if n < 0 else f"step-{n}"): _fluid(n, g["ratio"]) for n in (-1, 0, 1, 2, 3, 4, 5)}
    unit = 8 * g["air"]
    space = {f"space-{i}": round(unit * k, 1) for i, k in enumerate((.5, 1, 1.5, 2, 3, 5, 8, 13))}
    mot = {"still": (0, 0), "breath": (900, 5200), "drift": (1100, 7000)}[g["motion"]]
    longest = max(len(w) for w in job["brand"].split())
    mast_vw = round(min(19.0, 88 / (longest * .64)), 2)       # the longest brand word fits the viewport width
    return {"theme": th, "genome": dict(g), "color": col,
            "font": {"display": GROTESK, "body": SERIF if g["voice"] == "serif" else GROTESK, "mono": MONO},
            "type": steps, "mast-vw": mast_vw, "space": space,
            "motion": {"reveal-ms": mot[0], "breath-ms": mot[1], "kind": g["motion"],
                       "ease": "cubic-bezier(.2,.7,.1,1)"},
            "grid": {"cols": g["cols"], "tension": g["tension"]},
            "matter": [m.get("preset") or "concrete" for m in job["materials"]]}


def css_vars(t: dict) -> str:
    v = [f"--{k}:{c}" for k, c in t["color"].items()]
    v += [f"--{k}:{s[2]}" for k, s in t["type"].items()]
    v += [f"--{k}:{px / 16:.4f}rem" for k, px in t["space"].items()]
    v += [f"--font-display:{t['font']['display']}", f"--font-body:{t['font']['body']}", f"--font-mono:{t['font']['mono']}",
          f"--cols:{t['grid']['cols']}", f"--mast:{t['mast-vw']}vw",
          f"--reveal:{t['motion']['reveal-ms']}ms", f"--breath:{t['motion']['breath-ms']}ms", f"--ease:{t['motion']['ease']}"]
    return ":root{" + ";".join(v) + "}"


def dtcg(t: dict) -> dict:
    """W3C Design Tokens (Community Group format) view of the same tokens."""
    return {"color": {"$type": "color", **{k: {"$value": c} for k, c in t["color"].items()}},
            "fontFamily": {"$type": "fontFamily", **{k: {"$value": [s.strip('"') for s in f.split(",")]} for k, f in t["font"].items()}},
            "fontSize": {"$type": "dimension", **{k: {"$value": f"{s[1]}px", "$description": f"fluid {s[0]}-{s[1]} px, {s[2]}"} for k, s in t["type"].items()}},
            "space": {"$type": "dimension", **{k: {"$value": f"{px}px"} for k, px in t["space"].items()}},
            "duration": {"$type": "duration", "reveal": {"$value": f"{t['motion']['reveal-ms']}ms"}, "breath": {"$value": f"{t['motion']['breath-ms']}ms"}},
            "cubicBezier": {"$type": "cubicBezier", "ease": {"$value": [.2, .7, .1, 1]}},
            "$extensions": {"gentle_monster": {"genome": t["genome"], "theme": t["theme"], "matter": t["matter"]}}}
