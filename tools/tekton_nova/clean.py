"""Remove the draft text from the left of the TEKTON NOVA screen (user's own Photoshop artwork).

python3 tools/tekton_nova/clean.py  ->  out/tekton_nova/clean.jpg
Text pixels (bright, low-saturation, inside the text box) are filled from the surrounding sky by
normalized blur; the dark gradient laid over it in the draft hides what is left.
"""
import os
import numpy as np
from PIL import Image, ImageFilter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
src = Image.open(os.path.join(REPO, 'docs/tekton_nova/source_screen.jpg')).convert('RGB')
a = np.asarray(src, float)
H, W = a.shape[:2]
mx, mn = a.max(2), a.min(2)
box = np.zeros((H, W), bool); box[118:548, 95:840] = True
m = box & (mn > 150) & ((mx - mn) < 70)
mask = Image.fromarray((m * 255).astype('uint8')).filter(ImageFilter.MaxFilter(13))
m = np.asarray(mask, float) / 255
keep = 1 - m
def blur(x, r, passes=3):
    # repeated box blur (≈ gaussian), numpy only
    for _ in range(passes):
        for ax in (0, 1):
            c = np.cumsum(np.pad(x, [(r + 1, r) if i == ax else (0, 0) for i in range(2)], mode='edge'), axis=ax)
            x = (np.take(c, range(2 * r + 1, c.shape[ax]), axis=ax) - np.take(c, range(0, c.shape[ax] - 2 * r - 1), axis=ax)) / (2 * r + 1)
    return x
# fill from near to far: small radius where enough sky is close, larger radius inside big text blobs
fill = np.zeros_like(a); done = np.zeros((H, W))
for r in (6, 14, 30, 60):
    wk = blur(keep, r)
    f = np.dstack([blur(a[..., c] * keep, r) for c in range(3)]) / np.maximum(wk, 1e-6)[..., None]
    use = (wk > .12) * (1 - done)
    fill += f * use[..., None]; done += use
out = a * keep[..., None] + fill * m[..., None]
# put stars back where text was (same density as the sky around it)
rng = np.random.default_rng(3)
ys, xs = np.nonzero(m > .5)
pick = rng.random(len(ys)) < .0035
for y, x in zip(ys[pick], xs[pick]):
    r = rng.choice([0, 0, 0, 1])
    out[max(y - r, 0):y + r + 1, max(x - r, 0):x + r + 1] = 235 + rng.random() * 20
os.makedirs(os.path.join(REPO, 'out/tekton_nova'), exist_ok=True)
Image.fromarray(out.clip(0, 255).astype('uint8')).save(os.path.join(REPO, 'out/tekton_nova/clean.jpg'), quality=95)
print('ok', W, H, int(m.sum()))
