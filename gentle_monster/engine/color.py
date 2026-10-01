"""Colour arithmetic the engine and its judge share. WCAG 2.x relative luminance and contrast ratio.

Everything here is plain math on #rrggbb -- no CSS color-mix() reaches the page, so the colour the
browser computes is the colour this module wrote, and the judge can measure the same quantity twice
(here, from the tokens; in the browser, from computed styles). Two routes, one number.
"""
from __future__ import annotations


def rgb(h: str) -> "tuple[int, int, int]":
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def hexa(c) -> str:
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c[:3])


def mix(a: str, b: str, t: float) -> str:
    """a -> b by t (0 = a, 1 = b), in sRGB."""
    A, B = rgb(a), rgb(b)
    return hexa([A[i] + (B[i] - A[i]) * t for i in range(3)])


def luminance(h) -> float:
    c = rgb(h) if isinstance(h, str) else h
    lin = [(v / 255) / 12.92 if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4 for v in c[:3]]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def ensure(fg: str, bg: str, target: float) -> str:
    """The colour nearest to `fg` (walking toward black or white, whichever side of `bg` gives room)
    whose contrast with `bg` is at least `target`. Deterministic; returns fg itself if it already passes."""
    if contrast(fg, bg) >= target:
        return fg
    away = "#ffffff" if luminance(bg) < 0.18 else "#000000"
    for k in range(1, 51):
        c = mix(fg, away, k / 50)
        if contrast(c, bg) >= target:
            return c
    return away


def distance(a, b) -> float:
    A = rgb(a) if isinstance(a, str) else a
    B = rgb(b) if isinstance(b, str) else b
    return sum((A[i] - B[i]) ** 2 for i in range(3)) ** .5
