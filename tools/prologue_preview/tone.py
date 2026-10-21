"""PH-08 in one colour: the night street mapped onto an olive-green ramp, the red signal kept red.

python3 tools/prologue_preview/tone.py  ->  out/prologue_preview/ph08_tone.jpg
Only re-colours the applicant's own photo (no drawing). The ramp stops are the sheet's TONE swatches.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
SRC = os.path.join(REPO, 'docs/jaju_rounding_vmd/assets/photo/PH-08.jpg')
OUT = os.path.join(REPO, 'out/prologue_preview')
RAMP = [(0.0, '#0f1407'), (0.35, '#2f3a14'), (0.7, '#7d8a45'), (1.0, '#eef0dc')]   # shadow -> olive -> paper
RED = '#c8322b'


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)


def main():
    os.makedirs(OUT, exist_ok=True)
    im = Image.open(SRC).convert('RGB')
    a = np.asarray(im, float) / 255
    lum = (.299 * a[..., 0] + .587 * a[..., 1] + .114 * a[..., 2]) ** 1.15          # a little deeper in the dark
    xs = np.array([p for p, _ in RAMP]); cs = np.stack([hexrgb(c) for _, c in RAMP])
    out = np.stack([np.interp(lum, xs, cs[:, k]) for k in range(3)], -1)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = np.clip((r - np.maximum(g, b) * 1.6) * 4, 0, 1) * (r > .35)                  # only the strongly red pixels: the signal
    m = np.asarray(Image.fromarray((red * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.5)), float)[..., None] / 255
    out = out * (1 - m) + (hexrgb(RED) * (.55 + .45 * lum[..., None])) * m
    Image.fromarray(np.clip(out, 0, 255).astype('uint8')).save(os.path.join(OUT, 'ph08_tone.jpg'), quality=92)
    print('산출물: out/prologue_preview/ph08_tone.jpg')


if __name__ == '__main__':
    sys.exit(main())
