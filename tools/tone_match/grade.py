"""One colour grade for three of the applicant's photos, so the card row reads as one page.

python3 tools/tone_match/grade.py  ->  docs/tone_match/graded_*.jpg, compare.jpg
Re-colours only (no drawing, no generation): match brightness, then one shared look like the reference cards --
deep blacks, muted colour, teal-green shadows, warm highlights, light grain. The same steps work as a Lightroom preset.
"""
import os

import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
D = os.path.join(REPO, 'docs/tone_match')
SRC = ['src_cafe', 'src_shop', 'src_park']


def grade(a):
    lum = .299 * a[..., 0] + .587 * a[..., 1] + .114 * a[..., 2]
    a = a * (.42 / max(lum.mean(), 1e-3)) ** .6                         # 1. bring every photo to a similar exposure
    a = np.clip(a, 0, 1)
    lum = (.299 * a[..., 0] + .587 * a[..., 1] + .114 * a[..., 2])[..., None]
    a = lum + (a - lum) * .55                                            # 2. mute colour
    a = np.clip((a - .04) / .96, 0, 1) ** 1.12                           # 3. deeper blacks, a little contrast
    l = (.299 * a[..., 0] + .587 * a[..., 1] + .114 * a[..., 2])[..., None]
    sh, hi = (1 - l) ** 2, l ** 2
    a = a + sh * np.array([-.035, .015, .01]) + hi * np.array([.04, .015, -.03])   # 4. teal-green shadows, warm highlights
    a = a * .94 + .02                                                    # 5. soft film roll-off
    a = a + np.random.default_rng(1).normal(0, .012, a.shape[:2])[..., None]        # 6. light grain
    return np.clip(a, 0, 1)


def main():
    outs = []
    for n in SRC:
        im = Image.open(os.path.join(D, n + '.jpg')).convert('RGB')
        g = Image.fromarray((grade(np.asarray(im, float) / 255) * 255).astype('uint8'))
        g.save(os.path.join(D, n.replace('src', 'graded') + '.jpg'), quality=92); outs.append((im, g))
    h = 520; row = lambda ims: [i.resize((int(i.width * h / i.height), h)) for i in ims]
    top, bot = row([o[0] for o in outs]), row([o[1] for o in outs]); w = sum(i.width for i in top) + 40
    S = Image.new('RGB', (w, 2 * h + 30), (18, 63, 115)); x = 10
    for a, b in zip(top, bot):
        S.paste(a, (x, 10)); S.paste(b, (x, h + 20)); x += a.width + 10
    S.save(os.path.join(D, 'compare.jpg'), quality=88); print('산출물: docs/tone_match/compare.jpg · graded_*.jpg')


if __name__ == '__main__':
    main()
