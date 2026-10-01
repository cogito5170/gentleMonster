"""Measured facts about the images a user sends: photo mood, which image is a reference layout,
and what the reference layout looks like. Everything here is measured from pixels -- no model.

Numbers are on a 1000 px downscale:
  brightness   mean luma 0..1          dark    share of luma < 40/255
  saturation   mean HSV S 0..1         warmth  mean(R) - mean(B)
  contrast     std of luma             focus   centre edge variance / whole-frame edge variance
  strength     saturation x contrast x sqrt(edge variance) -- picks the cover
"""
from __future__ import annotations

from pathlib import Path


def _load(p, size=1000):
    from PIL import Image
    im = Image.open(p).convert("RGB")
    im.thumbnail((size, size))
    return im


def measure(p) -> dict:
    import numpy as np
    from PIL import ImageFilter
    im = _load(p)
    a = np.asarray(im).astype(float) / 255
    hsv = np.asarray(im.convert("HSV")).astype(float) / 255
    L = np.asarray(im.convert("L")).astype(float)
    e = np.asarray(im.convert("L").filter(ImageFilter.FIND_EDGES)).astype(float)
    h, w = L.shape
    ev = float(e.var()) or 1.0
    m = {"path": str(p), "w": im.width, "h": im.height, "aspect": round(im.width / im.height, 3),
         "brightness": round(float(L.mean() / 255), 3), "contrast": round(float(L.std() / 255), 3),
         "dark": round(float((L < 40).mean()), 3), "saturation": round(float(hsv[..., 1].mean()), 3),
         "warmth": round(float(a[..., 0].mean() - a[..., 2].mean()), 3),
         "focus": round(float(e[h // 3:2 * h // 3, w // 3:2 * w // 3].var()) / ev, 2)}
    m["mono"] = m["saturation"] < .03
    m["strength"] = round(m["saturation"] * m["contrast"] * (ev ** .5) / 10, 4)
    return m


def palette(p, n: int = 6) -> "list[tuple[str, float]]":
    from PIL import Image
    im = _load(p, 200)
    q = im.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    pal, tot = q.getpalette(), im.width * im.height
    return [("#%02x%02x%02x" % tuple(pal[i * 3:i * 3 + 3]), c / tot) for c, i in sorted(q.getcolors(), reverse=True)]


def reference_score(p) -> float:
    """How much an image looks like a layout/board screenshot rather than a photograph (0..1).
    Layout screenshots are mostly flat paper or flat frame colour with sharp rectangular edges;
    photographs have few perfectly flat regions. Measured: share of pixels in 8x8 blocks whose
    luma varies by less than 2/255."""
    import numpy as np
    L = np.asarray(_load(p, 800).convert("L")).astype(float)
    h, w = (L.shape[0] // 8) * 8, (L.shape[1] // 8) * 8
    B = L[:h, :w].reshape(h // 8, 8, w // 8, 8).transpose(0, 2, 1, 3).reshape(-1, 64)
    return round(float(((B.max(1) - B.min(1)) < 2).mean()), 3)


REF_THRESHOLD = 0.12      # measured: photos 0.000-0.001 (dark night shots included), a magazine-board screenshot 0.324


def split(images, text: str = "") -> "tuple[list[str], list[str]]":
    """(photos, references). A file name with ref/레퍼런스/참고/layout, or a flat-block score >= REF_THRESHOLD,
    makes an image a reference. If the text asks for a reference layout but none scores as one,
    the highest-scoring image is taken as the reference only when there are at least two images."""
    photos, refs, scored = [], [], []
    for p in images:
        name = Path(p).name.lower()
        s = reference_score(p)
        scored.append((s, p))
        if any(k in name for k in ("ref", "레퍼런스", "참고", "layout", "레이아웃")) or s >= REF_THRESHOLD:
            refs.append(str(p))
        else:
            photos.append(str(p))
    wants_ref = any(k in (text or "") for k in ("레퍼런스", "참고", "reference", "레이아웃처럼", "이 레이아웃", "이런 레이아웃"))
    if wants_ref and not refs and len(images) >= 2:
        s, p = max(scored)
        refs.append(str(p)); photos.remove(str(p))
    return photos, refs


def reference_style(p) -> dict:
    """What the reference layout looks like, measured. Used to set paper, margins and density of the moodboard."""
    import numpy as np
    im = _load(p, 800)
    a = np.asarray(im).astype(float)
    L = np.asarray(im.convert("L")).astype(float)
    hsv = np.asarray(im.convert("HSV")).astype(float) / 255
    h, w = L.shape
    border = np.concatenate([a[:h // 20].reshape(-1, 3), a[-h // 20:].reshape(-1, 3), a[:, :w // 20].reshape(-1, 3), a[:, -w // 20:].reshape(-1, 3)])
    paper = np.median(border, 0)
    near_paper = (np.abs(a - paper).sum(-1) < 24).mean()
    img_share = float(((hsv[..., 1] > .12) | (L < 60)).mean())
    sat = hsv[..., 1] > .45
    accent = "#%02x%02x%02x" % tuple(int(x) for x in np.median(a[sat], 0)) if sat.mean() > .004 else None
    dark_paper = paper.mean() < 90
    return {"paper": "#%02x%02x%02x" % tuple(int(x) for x in paper), "dark_paper": bool(dark_paper),
            "whitespace": round(float(near_paper), 3), "image_share": round(img_share, 3), "accent": accent,
            "density": "airy" if near_paper > .55 else ("dense" if near_paper < .3 else "balanced"),
            "reference_score": reference_score(p)}
