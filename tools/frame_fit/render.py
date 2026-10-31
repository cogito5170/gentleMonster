"""Fit the applicant's photos into the corner frame without stretching.

python3 tools/frame_fit/render.py  ->  docs/frame_fit/opt_{now,a,b,c}.jpg and flat_{a,b,c}.jpg

The frame (docs/frame_fit/current.jpg) shows two walls meeting at a corner in the middle. Measured on the frame:
corner height 759 px, outer edges 470 px, half widths 686 px. For a 90-degree corner seen head-on this gives each
wall a true shape of about 2.06 : 1, so both walls together want a 4.13 : 1 picture. PH-01 is 1.78 : 1, which is why
it looks stretched sideways (x 2.3). Each option below makes a 4.13 : 1 strip from the photos only (crop, place,
or two photos side by side) and lays each half onto its wall with an exact plane homography.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
D = os.path.join(REPO, 'docs/frame_fit')

# photo opening of the frame, read off current.jpg (1806 x 1008)
LEFT = [(247, 330), (933, 103), (933, 862), (250, 800)]     # TL TR BR BL
RIGHT = [(933, 103), (1617, 328), (1615, 796), (933, 862)]


def wall_aspect():
    hc = LEFT[2][1] - LEFT[1][1]; he = ((LEFT[3][1] - LEFT[0][1]) + (RIGHT[2][1] - RIGHT[1][1])) / 2
    half = ((LEFT[1][0] - LEFT[0][0]) + (RIGHT[1][0] - RIGHT[0][0])) / 2
    k = hc / he; s = math.sin(math.radians(45))                 # 90-degree corner, walls at 45 degrees
    w_over_d = (k - 1) / s; f = half * k / (w_over_d * s)       # edge x = f * W cos45 / (k d)
    h_over_d = hc / f
    return w_over_d / h_over_d, hc, he, half, f


ASPECT, HC, HE, HALF, FOCAL = wall_aspect()
PANO = 2 * ASPECT


def homography(src, dst):
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y, -u], [0, 0, 0, x, y, 1, -v * x, -v * y, -v]]
    h = np.linalg.svd(np.array(A, float))[2][-1]
    return (h / h[-1]).reshape(3, 3)


def onto_frame(strip, out):
    """Lay the left half of `strip` on the left wall and the right half on the right wall."""
    base = Image.open(os.path.join(D, 'current.jpg')).convert('RGB'); W, H = strip.size
    for quad, x0 in ((LEFT, 0), (RIGHT, W / 2)):
        src = [(x0, 0), (x0 + W / 2, 0), (x0 + W / 2, H), (x0, H)]
        Hm = homography(quad, src)
        warped = strip.transform(base.size, Image.PERSPECTIVE, tuple(Hm.flatten()[:8]), Image.BICUBIC)
        m = Image.new('L', base.size, 0); ImageDraw.Draw(m).polygon(quad, fill=255)
        base.paste(warped, (0, 0), m)
    d = ImageDraw.Draw(base); d.line([LEFT[1], LEFT[2]], fill=(255, 255, 255), width=1)   # the corner edge
    base.save(os.path.join(D, out), quality=90)
    base.crop((170, 30, 1700, 930)).save(os.path.join(D, out.replace('.jpg', '_c.jpg')), quality=90)   # frame only, for the sheet


def hatch(im, box):
    """Mark an area to be filled by generative expand (a diagram marker, not picture content)."""
    x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    t = Image.new('RGB', (w, h), (38, 52, 70)); d = ImageDraw.Draw(t)
    for k in range(-h, w, 28):
        d.line([(k, h), (k + h, 0)], fill=(90, 110, 135), width=3)
    d.rectangle((0, 0, w - 1, h - 1), outline=(255, 107, 91), width=4); im.paste(t, (x0, y0))


def main():
    p01 = Image.open(os.path.join(D, 'PH-01.jpg')).convert('RGB'); p03 = Image.open(os.path.join(D, 'PH-03.jpg')).convert('RGB')

    # now: the whole of PH-01 (top 620 px) squeezed onto both walls, for comparison
    onto_frame(p01.crop((0, 0, 1500, 620)), 'opt_now.jpg')

    # A: one photo, cropped to the panorama shape; the fold falls in the gap right of the standing man
    w = 1300; h = round(w / PANO); a = p01.crop((200, 230, 200 + w, 230 + h)); a.save(os.path.join(D, 'flat_a.jpg'), quality=90); onto_frame(a, 'opt_a.jpg')

    # B: one photo kept whole (sand trimmed), placed on a panorama canvas; the sides are left for generative expand
    ph = p01.crop((0, 60, 1500, 680)); H = ph.height; Wc = round(H * PANO); x0 = Wc // 2 - 880
    b = Image.new('RGB', (Wc, H)); b.paste(ph, (x0, 0)); hatch(b, (0, 0, x0, H)); hatch(b, (x0 + 1500, 0, Wc, H))
    b.save(os.path.join(D, 'flat_b.jpg'), quality=90); onto_frame(b, 'opt_b.jpg')

    # C: two photos, one per wall, each cropped to the wall shape with the horizon at 48 % so it meets at the corner
    def wall(im, x0, cw, horizon):                       # crop to the wall shape with the horizon at 48 %
        ch = round(cw / ASPECT); y0 = horizon - round(.48 * ch); return im.crop((x0, y0, x0 + cw, y0 + ch))
    right = wall(p01, 250, 1250, 354); left = wall(p03, 0, 1500, 413).resize(right.size, Image.LANCZOS)
    c = Image.new('RGB', (right.width * 2, right.height)); c.paste(left, (0, 0)); c.paste(right, (right.width, 0))
    c.save(os.path.join(D, 'flat_c.jpg'), quality=90); onto_frame(c, 'opt_c.jpg')

    print(f'wall {ASPECT:.2f}:1 · panorama {PANO:.2f}:1 · PH-01 {1500/844:.2f}:1 · stretch now x{PANO/(1500/620):.2f} (top 620 px) / x{PANO/(1500/844):.2f} (whole)')
    print(f'A crop {w}x{h} · B canvas {Wc}x{H}, photo at x {x0} · C each wall {right.width}x{right.height}')


if __name__ == '__main__':
    main()
