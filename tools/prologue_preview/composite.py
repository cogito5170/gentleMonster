"""Lay the flat Prologue spread onto the Codex mock-up of a hand-held open book (preview only).

python3 tools/prologue_preview/composite.py <mockup.png> <corners.json> <out.jpg>
corners.json: for each page, the image points of its top edge and bottom edge from the outer edge to the gutter
(left page) or from the gutter to the outer edge (right page), the same number of points on both edges; the page is cut
into strips between them and each strip is warped on its own, so a gentle curl follows. The art is multiplied onto the
paper so the mock-up's light, shadow and green cast stay.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter  # noqa: E401

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
PAPER = np.array([0xf1, 0xee, 0xe6], float)


def page_map(top, bot, x0, half, Hh, size, rows=32):
    """Per-pixel source coordinates for one page: a mesh between the top and bottom edge points, split into
    triangles, each mapped affinely -- piecewise linear, so neighbouring cells meet without seams."""
    W, H = size; sx = np.full((H, W), np.nan); sy = np.full((H, W), np.nan)
    top, bot = np.array(top, float), np.array(bot, float); n = len(top) - 1
    P = lambda i, j: top[i] * (1 - j / rows) + bot[i] * (j / rows)
    F = lambda i, j: np.array([x0 + half * i / n, Hh * j / rows])
    for i in range(n):
        for j in range(rows):
            for tri in (((i, j), (i + 1, j), (i + 1, j + 1)), ((i, j), (i + 1, j + 1), (i, j + 1))):
                a, b, c = (P(*t) for t in tri); fa, fb, fc = (F(*t) for t in tri)
                M = np.array([[b[0] - a[0], c[0] - a[0]], [b[1] - a[1], c[1] - a[1]]])
                if abs(np.linalg.det(M)) < 1e-9:
                    continue
                Mi = np.linalg.inv(M)
                x_lo, x_hi = int(max(0, np.floor(min(a[0], b[0], c[0])))), int(min(W, np.ceil(max(a[0], b[0], c[0])) + 1))
                y_lo, y_hi = int(max(0, np.floor(min(a[1], b[1], c[1])))), int(min(H, np.ceil(max(a[1], b[1], c[1])) + 1))
                if x_lo >= x_hi or y_lo >= y_hi:
                    continue
                yy, xx = np.mgrid[y_lo:y_hi, x_lo:x_hi]
                u = Mi[0, 0] * (xx - a[0]) + Mi[0, 1] * (yy - a[1]); v = Mi[1, 0] * (xx - a[0]) + Mi[1, 1] * (yy - a[1])
                inside = (u >= -1e-6) & (v >= -1e-6) & (u + v <= 1 + 1e-6)
                fx = fa[0] + u * (fb[0] - fa[0]) + v * (fc[0] - fa[0]); fy = fa[1] + u * (fb[1] - fa[1]) + v * (fc[1] - fa[1])
                sx[y_lo:y_hi, x_lo:x_hi][inside] = fx[inside]; sy[y_lo:y_hi, x_lo:x_hi][inside] = fy[inside]
    return sx, sy


def sample(img, sx, sy):
    """Bilinear lookup of img at (sx, sy); NaN -> 0 with zero coverage."""
    a = np.asarray(img, float); H, W = a.shape[:2]; ok = ~np.isnan(sx)
    x = np.clip(np.nan_to_num(sx), 0, W - 1.001); y = np.clip(np.nan_to_num(sy), 0, H - 1.001)
    x0, y0 = x.astype(int), y.astype(int); dx, dy = (x - x0)[..., None], (y - y0)[..., None]
    v = (a[y0, x0] * (1 - dx) * (1 - dy) + a[y0, x0 + 1] * dx * (1 - dy) + a[y0 + 1, x0] * (1 - dx) * dy + a[y0 + 1, x0 + 1] * dx * dy)
    return v, ok.astype(float)


def main(mock_path, corners_path, out_path):
    mock = Image.open(mock_path).convert('RGB'); size = mock.size
    spread = Image.open(os.path.join(REPO, 'out/prologue_preview/spread.png')).convert('RGB').filter(ImageFilter.GaussianBlur(1.2))
    W, Hh = spread.size; half = W / 2
    C = json.load(open(corners_path))
    base = np.asarray(mock, float); acc = np.zeros_like(base); cover = np.zeros(base.shape[:2])
    for side, x0 in (('left', 0.0), ('right', half)):
        sx, sy = page_map(C[side]['top'], C[side]['bottom'], x0, half, Hh, size)
        v, ok = sample(spread, sx, sy); acc += v * ok[..., None]; cover = np.maximum(cover, ok)
    cover = np.asarray(Image.fromarray((cover * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(.7)), float) / 255
    for poly in C.get('exclude', []):                       # the thumb and fingers stay in front of the page
        m = Image.new('L', size, 0); ImageDraw.Draw(m).polygon([tuple(p) for p in poly], fill=255)
        cover *= 1 - np.asarray(m.filter(ImageFilter.GaussianBlur(2.5)), float) / 255
    cover = np.clip(cover, 0, 1)[..., None]; art = np.where(acc > 0, acc, PAPER)
    factor = np.clip(art / PAPER, 0, 1.04)                   # paper-coloured art leaves the mock-up paper as it is
    out = base * (1 - cover) + base * factor * cover
    img = Image.fromarray(np.clip(out, 0, 255).astype('uint8'))
    fb = C.get('farBlur')                                    # the far end of the right page is out of focus in the mock-up
    if fb:
        (ax, ay), (bx, by) = fb['from'], fb['to']; vx, vy = bx - ax, by - ay
        yy, xx = np.mgrid[0:size[1], 0:size[0]]
        wgt = np.clip(((xx - ax) * vx + (yy - ay) * vy) / (vx * vx + vy * vy), 0, 1)
        soft = np.asarray(img.filter(ImageFilter.GaussianBlur(fb['r'])), float)
        img = Image.fromarray((np.asarray(img, float) * (1 - wgt[..., None]) + soft * wgt[..., None]).astype('uint8'))
    img.save(out_path, quality=92)
    print('산출물: ' + os.path.relpath(out_path, REPO))


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:4]))
