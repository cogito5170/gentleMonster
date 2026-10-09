"""Vintage print stage: render -> grid collage -> 6-colour dither -> drawing layer -> sharp type.

The inks come from the mood reference (an indexed, error-diffused image: #110f08 #3e3e39 #5a7e91 #848484
#b0afa6 #ceccbe). Its blue is replaced by a mid grey (#5f5f5b) so the sheets stay grey; one red (#a8392c)
is kept for the stop light only.
Small type and the architectural drawing layer are drawn AFTER the dither so they stay crisp.

python -m gentle_monster.relief.post <page> <dir> [--exposures a.png:x,y,w,h:opacity ...]
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ASSETS = Path(os.environ.get("RELIEF_ASSETS", Path(__file__).with_name("assets")))
INKS = ["#110f08", "#3e3e39", "#5f5f5b", "#848484", "#b0afa6", "#ceccbe", "#a8392c"]
GRID = 15  # module in page mm (architect's grid: 14 x 19.8 modules on A4)


def rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def palette_image(inks=INKS):
    pal = []
    for h in inks:
        pal += rgb(h)
    pal += [0] * (768 - len(pal))
    p = Image.new("P", (1, 1)); p.putpalette(pal); return p


def tone(im: Image.Image, lift=0.0, gamma=1.0, contrast=1.0, sat=1.0):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    a = lift + (1 - lift) * np.power(a, gamma)
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    out = ImageEnhance.Contrast(out).enhance(contrast)
    return ImageEnhance.Color(out).enhance(sat)


def expose(base: Image.Image, layer: Image.Image, box, opacity=0.5, mode="screen"):
    """Double exposure inside a page-mm rectangle snapped to the grid."""
    W = base.width; s = W / 210
    x, y, w, h = [round(v * s) for v in box]
    lay = layer.convert("RGB").resize((w, h), Image.LANCZOS)
    a = np.asarray(base.crop((x, y, x + w, y + h))).astype(np.float32) / 255
    b = np.asarray(lay).astype(np.float32) / 255
    m = 1 - (1 - a) * (1 - b) if mode == "screen" else (a * b if mode == "multiply" else np.maximum(a, b))
    mix = a * (1 - opacity) + m * opacity
    base.paste(Image.fromarray((mix * 255).astype(np.uint8)), (x, y))
    return base


GRADE = [(0.00, "#110f08"), (0.22, "#3e3e39"), (0.42, "#5f5f5b"), (0.60, "#848484"), (0.80, "#b0afa6"), (0.93, "#ceccbe")]


def grade(im: Image.Image, amount=0.85):
    """Gradient map on luminance through the six inks: shadows warm black, mid-tones blue, highlights paper."""
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    L = a @ np.array([0.299, 0.587, 0.114], np.float32)
    xs = np.array([g[0] for g in GRADE]); cs = np.array([rgb(g[1]) for g in GRADE], np.float32) / 255
    g = np.stack([np.interp(L, xs, cs[:, i]) for i in range(3)], -1)
    return Image.fromarray((np.clip(a * (1 - amount) + g * amount, 0, 1) * 255).astype(np.uint8))


def redness(im: Image.Image, lo=0.38, hi=0.6):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    r = a[..., 0] - np.maximum(a[..., 1], a[..., 2])
    return np.clip((r - lo) / (hi - lo), 0, 1)


def dither(im: Image.Image, red_mask=None, inks=INKS):
    """Error-diffuse to the six inks; the red ink is allowed only where the render is truly red."""
    six = im.convert("RGB").quantize(palette=palette_image(inks[:6]), dither=Image.Dither.FLOYDSTEINBERG).convert("RGB")
    if red_mask is None or red_mask.max() <= 0:
        return six
    seven = im.convert("RGB").quantize(palette=palette_image(inks), dither=Image.Dither.FLOYDSTEINBERG).convert("RGB")
    m = (red_mask > np.random.default_rng(1).random(red_mask.shape))[..., None]
    return Image.fromarray(np.where(m, np.asarray(seven), np.asarray(six)))


def font(file, px):
    return ImageFont.truetype(str(ASSETS / "fonts" / file), max(1, round(px)))


def draw_runs(im: Image.Image, runs):
    d = ImageDraw.Draw(im); s = im.width / 210
    for r in runs:
        f = font(r["font"], r["size"] * s)
        track = r.get("track", 0.0) * r["size"] * s
        lead = r.get("leading", 1.25) * r["size"] * s
        col = rgb(r.get("color", INKS[0]))
        for i, line in enumerate(r["s"].split("\n")):
            y = r["y"] * s + i * lead
            wline = sum(d.textlength(ch, font=f) + track for ch in line) - (track if line else 0)
            x = r["x"] * s - (wline if r.get("align") == "RIGHT" else wline / 2 if r.get("align") == "CENTER" else 0)
            for ch in line:
                d.text((x, y), ch, font=f, fill=col, anchor="ls")
                x += d.textlength(ch, font=f) + track
    return im


def draw_lines(im: Image.Image, lines):
    """Architectural layer: {'kind':'grid'|'dim'|'rule'|'crop'|'axis', ...} in page mm."""
    d = ImageDraw.Draw(im); s = im.width / 210; ink = rgb(INKS[0])
    for L in lines:
        k = L["kind"]; c = rgb(L.get("color", INKS[0])); wd = max(1, round(L.get("w", 0.15) * s))
        if k == "grid":
            for gx in range(0, 211, GRID):
                if L.get("cols", True):
                    d.line([(gx * s, L.get("y0", 0) * s), (gx * s, L.get("y1", 297) * s)], fill=c, width=1)
            for gy in range(0, 298, GRID):
                if L.get("rows", True):
                    d.line([(L.get("x0", 0) * s, gy * s), (L.get("x1", 210) * s, gy * s)], fill=c, width=1)
        elif k == "seg":
            d.line([(L["x0"] * s, L["y0"] * s), (L["x1"] * s, L["y1"] * s)], fill=c, width=wd)
        elif k == "circle":
            r = L["r"] * s
            d.ellipse([L["cx"] * s - r, L["cy"] * s - r, L["cx"] * s + r, L["cy"] * s + r], outline=c, width=wd)
        elif k == "rule":
            d.line([(L["x0"] * s, L["y0"] * s), (L["x1"] * s, L["y1"] * s)], fill=c, width=wd)
        elif k == "dim":  # dimension line with ticks and a label in the middle
            x0, y0, x1, y1 = (L[v] * s for v in ("x0", "y0", "x1", "y1"))
            d.line([(x0, y0), (x1, y1)], fill=c, width=1)
            for (x, y) in ((x0, y0), (x1, y1)):
                d.line([(x - 1.6 * s, y + 1.6 * s), (x + 1.6 * s, y - 1.6 * s)], fill=c, width=max(1, round(0.25 * s)))
                if y0 == y1:
                    d.line([(x, y - 2.2 * s), (x, y + 2.2 * s)], fill=c, width=1)
                else:
                    d.line([(x - 2.2 * s, y), (x + 2.2 * s, y)], fill=c, width=1)
            if L.get("label"):
                f = font("ArchivoExp-Reg.ttf", 2.2 * s)
                mx, my = (x0 + x1) / 2, (y0 + y1) / 2
                tw = d.textlength(L["label"], font=f)
                if y0 == y1:
                    d.rectangle([mx - tw / 2 - 1.2 * s, my - 1.6 * s, mx + tw / 2 + 1.2 * s, my + 1.6 * s], fill=rgb(L.get("bg", INKS[5])))
                    d.text((mx, my), L["label"], font=f, fill=c, anchor="mm")
                else:
                    t = Image.new("RGBA", (int(tw + 3 * s), int(3.2 * s)), rgb(L.get("bg", INKS[5])) + (255,))
                    ImageDraw.Draw(t).text((t.width / 2, t.height / 2), L["label"], font=f, fill=c, anchor="mm")
                    t = t.rotate(90, expand=True); im.paste(t, (int(mx - t.width / 2), int(my - t.height / 2)), t)
        elif k == "crop":
            m = L.get("m", 6) * s; n = L.get("n", 4) * s; W, H = im.size
            for (x, y, sx, sy) in ((m, m, -1, -1), (W - m, m, 1, -1), (m, H - m, -1, 1), (W - m, H - m, 1, 1)):
                d.line([(x + sx * 1.5, y), (x + sx * n, y)], fill=c, width=1); d.line([(x, y + sy * 1.5), (x, y + sy * n)], fill=c, width=1)
        elif k == "axis":  # centre-line: dash-dot
            x0, y0, x1, y1 = (L[v] * s for v in ("x0", "y0", "x1", "y1"))
            n = int(max(abs(x1 - x0), abs(y1 - y0)) / (6 * s))
            for i in range(n):
                t0, t1 = i / n, (i + 0.55) / n
                d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], fill=c, width=1)
                t2 = (i + 0.75) / n
                d.point((x0 + (x1 - x0) * t2, y0 + (y1 - y0) * t2), fill=c)
    return im


def finish(render_png, runs, lines=(), exposures=(), toning=None, out=None):
    im = Image.open(render_png).convert("RGB")
    im = tone(im, **(toning or dict(lift=0.04, gamma=1.05, contrast=1.08, sat=0.85)))
    for e in exposures:
        expose(im, Image.open(e["src"]), e["box"], e.get("opacity", 0.5), e.get("mode", "screen"))
    red = redness(im)
    im = grade(im)
    im = dither(im, red)
    im = draw_lines(im, lines)
    im = draw_runs(im, runs)
    if out:
        im.save(out, quality=92)
    return im


if __name__ == "__main__":
    name, d = sys.argv[1], Path(sys.argv[2])
    spec = json.loads((d / f"{name}.json").read_text(encoding="utf-8"))
    runs = spec["runs"] if isinstance(spec, dict) else spec
    lines = spec.get("lines", []) if isinstance(spec, dict) else []
    exps = spec.get("exposures", []) if isinstance(spec, dict) else []
    for e in exps:
        e["src"] = str(d / e["src"])
    finish(d / f"{name}.png", runs, lines, exps, spec.get("toning") if isinstance(spec, dict) else None, out=d / f"{name}_final.png")
    print("ok", d / f"{name}_final.png")
