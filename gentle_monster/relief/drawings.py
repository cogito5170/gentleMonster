"""Architectural drawings the sets hang on their walls (drawn flat, then mounted as prints in 3D).

plan_titan.png: plan 1:200 of The Synthetic Titan (the applicant's Gentle Monster store synopsis):
an entrance of breathing steel joints, a central void with the android head, a forest of metal trees,
and the visitor's path drawn as a dashed line through the three zones.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import os
ASSETS = Path(os.environ.get("RELIEF_ASSETS", Path(__file__).with_name("assets")))
INK = (17, 15, 8); PAPER = (226, 223, 213); GREY = (132, 132, 132); RED = (168, 57, 44)


def plan_titan(out, S=1200):
    im = Image.new("RGB", (S, S), PAPER); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(str(ASSETS / "fonts" / "ArchivoExp-Reg.ttf"), int(S * 0.018))
    m = S * 0.1; W = S - 2 * m
    wall = int(S * 0.012)
    d.rectangle([m, m, m + W, m + W], outline=INK, width=wall)
    d.rectangle([m + W * 0.42, m + W - wall, m + W * 0.58, m + W + wall], fill=PAPER)        # entrance
    for i in range(1, 8):                                                                     # breathing joints
        x = m + W * (0.18 + i * 0.08); d.line([(x, m + W * 0.86), (x, m + W * 0.94)], fill=INK, width=3)
    cx, cy, r = m + W * 0.5, m + W * 0.45, W * 0.2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    for k in range(18):                                                                       # hatch: the void
        y = cy - r + k * (2 * r / 18); dx = math.sqrt(max(r * r - (y - cy) ** 2, 0))
        d.line([(cx - dx, y), (cx + dx, y)], fill=GREY, width=1)
    d.ellipse([cx - W * 0.035, cy - W * 0.045, cx + W * 0.035, cy + W * 0.045], fill=INK)    # the head
    for (u, v) in [(0.14, 0.18), (0.2, 0.3), (0.12, 0.42), (0.82, 0.2), (0.88, 0.34), (0.8, 0.5), (0.86, 0.62), (0.16, 0.6)]:
        x, y = m + W * u, m + W * v; d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=INK, width=3); d.line([(x - 15, y), (x + 15, y)], fill=INK, width=1)
    path = [(0.5, 1.0), (0.5, 0.84), (0.26, 0.74), (0.2, 0.5), (0.32, 0.24), (0.5, 0.18), (0.7, 0.26), (0.78, 0.5), (0.68, 0.72), (0.56, 0.66)]
    pts = [(m + W * u, m + W * v) for u, v in path]
    for a, b in zip(pts, pts[1:]):
        n = int(math.dist(a, b) / 18)
        for i in range(n):
            t0, t1 = i / n, (i + 0.55) / n
            d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=RED, width=4)
    d.ellipse([pts[-1][0] - 10, pts[-1][1] - 10, pts[-1][0] + 10, pts[-1][1] + 10], fill=RED)
    for txt, (u, v) in [("ENTRANCE — BREATH", (0.5, 0.97)), ("VOID — TITAN", (0.5, 0.71)), ("FOREST — COLLECT", (0.16, 0.08))]:
        d.text((m + W * u, m + W * v), txt, font=f, fill=INK, anchor="mm")
    sx = m; sy = S - m * 0.45
    for i in range(5):
        d.rectangle([sx + i * W * 0.06, sy, sx + (i + 1) * W * 0.06, sy + 10], fill=INK if i % 2 == 0 else PAPER, outline=INK)
    d.text((sx + W * 0.32, sy + 5), "0   5   10 M", font=f, fill=INK, anchor="lm")
    nx, ny = m + W - 30, S - m * 0.5
    d.polygon([(nx, ny - 34), (nx - 12, ny + 4), (nx + 12, ny + 4)], fill=INK); d.text((nx, ny + 22), "N", font=f, fill=INK, anchor="mm")
    im.save(out)


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    plan_titan(out / "plan_titan.png")
    print("ok")
