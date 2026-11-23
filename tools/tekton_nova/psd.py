"""TEKTON NOVA screen as a layered Photoshop file (3960 x 1300 px = the 1980 x 650 artwork at 2x).

python3 tools/tekton_nova/clean.py && node tools/tekton_nova/build.mjs && python3 tools/tekton_nova/psd.py

  docs/tekton_nova/photoshop/tekton_nova_screen.psd   layers, bottom to top:
      Background (old text removed) · Original screen (hidden) · Shade - left gradient · TEKTON logo
      COPY (raster preview): Eyebrow, Headline, Body 1, Subhead, Body 2, Footer line, Footer text
  docs/tekton_nova/photoshop/live_text.jsx            run in Photoshop with the PSD open (File > Scripts > Browse):
      adds COPY (live text) — editable type layers at the same positions — and hides the raster preview
  docs/tekton_nova/tekton_nova_screen_photoshop.zip   both, plus the preview JPG

The PSD writer below is self-contained (no psd library was installable here): 8-bit RGB, PackBits (RLE)
channels, groups via 'lsct', unicode names via 'luni', 72 ppi resolution resource, merged composite.
"""
import json
import os
import struct
import zipfile

import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
DOC = os.path.join(REPO, 'docs/tekton_nova')
OUTD = os.path.join(DOC, 'photoshop')
LD = os.path.join(REPO, 'out/tekton_nova/layers')
S = 2
W, H = 1980 * S, 650 * S
ORANGE = (255, 138, 61)


# ── PackBits ─────────────────────────────────────────────────────────────────────────
def packbits(row):
    n = len(row)
    out = bytearray()
    if n == 0:
        return bytes(out)
    change = np.flatnonzero(np.diff(row)) + 1
    starts = np.concatenate([[0], change]); ends = np.concatenate([change, [n]])
    long = (ends - starts) >= 3
    pos = 0

    def literal(a, b):
        for c in range(a, b, 128):
            k = min(128, b - c)
            out.append(k - 1); out.extend(row[c:c + k].tobytes())

    for s, e in zip(starts[long], ends[long]):
        literal(pos, s)
        v, L = int(row[s]), e - s
        while L > 0:
            k = min(L, 128)
            if k < 3:
                literal(e - L, e); break
            out.append(257 - k); out.append(v); L -= k
        pos = e
    literal(pos, n)
    return bytes(out)


def rle_plane(plane):
    rows = [packbits(r) for r in plane]
    return struct.pack(f'>{len(rows)}H', *[len(r) for r in rows]), b''.join(rows)


# ── layers ───────────────────────────────────────────────────────────────────────────
def full(img):
    return Image.open(img).convert('RGB').resize((W, H), Image.LANCZOS)


def layer(name, rgba, x=0, y=0, hidden=False, opacity=255):
    a = np.asarray(rgba.convert('RGBA'))
    return dict(name=name, data=a, x=x, y=y, hidden=hidden, opacity=opacity)


def shade():
    t = np.linspace(0, 1, W)
    alpha = np.interp(t, [0, .28, .42, .56, 1], [.88, .80, .45, 0, 0])
    a = np.zeros((H, W, 4), np.uint8); a[..., 3] = (alpha * 255).round().astype(np.uint8)[None, :]
    return Image.fromarray(a, 'RGBA')


def ink_box(rgba, ox, oy, mask=None):
    al = np.asarray(rgba)[..., 3] > 40
    if mask is not None:
        al &= mask
    ys, xs = np.nonzero(al)
    return dict(l=int(ox + xs.min()), t=int(oy + ys.min()), r=int(ox + xs.max() + 1), b=int(oy + ys.max() + 1))


def build_layers():
    src = os.path.join(DOC, 'source_screen.jpg')
    L = [layer('Background (old text removed)', full(os.path.join(REPO, 'out/tekton_nova/clean.jpg'))),
         layer('Original screen (with old text)', full(src), hidden=True),
         layer('Shade - left gradient', shade())]
    logo = Image.open(src).convert('RGB').crop((30, 20, 280, 96)).resize((250 * S, 76 * S), Image.LANCZOS)
    L.append(layer('TEKTON logo', logo, 30 * S, 20 * S))
    meta = json.load(open(os.path.join(LD, 'boxes.json')))['boxes']
    names = dict(eyebrow='Eyebrow', headline='Headline', body1='Body 1', subhead='Subhead', body2='Body 2', footline='Footer line', foottext='Footer text')
    group, targets = [], {}
    for k, nm in names.items():
        b = meta[k]
        im = Image.open(os.path.join(LD, k + '.png')).convert('RGBA')
        ox, oy = b['x'] * S, b['y'] * S
        group.append(layer(nm, im, ox, oy))
        if k == 'eyebrow':
            a = np.asarray(im).astype(int)
            orange = (a[..., 0] > 180) & (a[..., 1] < 190) & (a[..., 2] < 140) & (a[..., 0] - a[..., 2] > 70)
            cols = np.flatnonzero(orange.any(0)); split = cols.min() - 4
            left = np.zeros(orange.shape, bool); left[:, :split] = True
            targets['eyebrow_a'] = ink_box(im, ox, oy, left)
            targets['eyebrow_b'] = ink_box(im, ox, oy, ~left)
        elif k != 'footline':
            targets[k] = ink_box(im, ox, oy)
    return L, group, targets


# ── PSD writer ───────────────────────────────────────────────────────────────────────
def pascal(name, pad=4):
    b = name.encode('ascii', 'replace')[:255]
    s = bytes([len(b)]) + b
    return s + b'\0' * ((-len(s)) % pad)


def info_block(key, data):
    data += b'\0' * ((-len(data)) % 4)
    return b'8BIM' + key + struct.pack('>I', len(data)) + data


def luni(name):
    u = name.encode('utf-16-be')
    return info_block(b'luni', struct.pack('>I', len(name)) + u)


def record_and_data(ly):
    """(layer record bytes, channel data bytes)"""
    if ly.get('section') is not None:
        top = left = bottom = right = 0
        chans = [(cid, struct.pack('>H', 0)) for cid in (-1, 0, 1, 2)]
        flags = 0x18 | (0x02 if ly.get('hidden') else 0)
        extra = info_block(b'lsct', struct.pack('>I', ly['section']))
    else:
        a = ly['data']; h, w = a.shape[:2]
        top, left, bottom, right = ly['y'], ly['x'], ly['y'] + h, ly['x'] + w
        chans = []
        for cid, ci in ((-1, 3), (0, 0), (1, 1), (2, 2)):
            counts, data = rle_plane(np.ascontiguousarray(a[..., ci]))
            chans.append((cid, struct.pack('>H', 1) + counts + data))
        flags = 0x08 | (0x02 if ly['hidden'] else 0)
        extra = b''
    rec = struct.pack('>4i', top, left, bottom, right) + struct.pack('>H', len(chans))
    rec += b''.join(struct.pack('>hI', cid, len(d)) for cid, d in chans)
    rec += b'8BIMnorm' + struct.pack('>BBBB', ly.get('opacity', 255), 0, flags, 0)
    ext = struct.pack('>I', 0) + struct.pack('>I', 0) + pascal(ly['name']) + luni(ly['name']) + extra
    rec += struct.pack('>I', len(ext)) + ext
    return rec, b''.join(d for _, d in chans)


def write_psd(path, layers, merged):
    recs, datas = zip(*[record_and_data(l) for l in layers])
    li = struct.pack('>h', len(layers)) + b''.join(recs) + b''.join(datas)
    li += b'\0' * ((-len(li)) % 4)
    lmi = struct.pack('>I', len(li)) + li + struct.pack('>I', 0)
    res = b'8BIM' + struct.pack('>H', 1005) + b'\0\0' + struct.pack('>I', 16) + struct.pack('>IHHIHH', 72 << 16, 1, 1, 72 << 16, 1, 1)
    m = np.asarray(merged.convert('RGB'))
    planes = [rle_plane(np.ascontiguousarray(m[..., c])) for c in range(3)]
    with open(path, 'wb') as f:
        f.write(b'8BPS' + struct.pack('>H', 1) + b'\0' * 6 + struct.pack('>HIIHH', 3, H, W, 8, 3))
        f.write(struct.pack('>I', 0))
        f.write(struct.pack('>I', len(res)) + res)
        f.write(struct.pack('>I', len(lmi)) + lmi)
        f.write(struct.pack('>H', 1) + b''.join(c for c, _ in planes) + b''.join(d for _, d in planes))


# ── JSX: live type layers on top of the raster preview ───────────────────────────────
TEXT = [  # key, layer name, contents, font, size, leading, tracking, rgb, opacity
    ('eyebrow_a', 'Eyebrow', 'INTRODUCING', 'Inter-SemiBold', 28, 0, 320, (255, 255, 255), 72),
    ('eyebrow_b', 'Eyebrow - product', 'TEKTON NOVA', 'Inter-SemiBold', 28, 0, 320, ORANGE, 100),
    ('headline', 'Headline', 'A Universe\rIn Your Hand.', 'InterDisplay-Bold', 132, 129, -25, (255, 255, 255), 100),
    ('body1', 'Body 1', 'Designed from the edge of light to the curve of glass,\rNOVA brings the depth of the night sky\rto the screen you hold every day.', 'Inter-Regular', 38, 56, 0, (255, 255, 255), 86),
    ('subhead', 'Subhead', 'Crafted Form. Endless Display.', 'Inter-SemiBold', 40, 0, -5, ORANGE, 100),
    ('body2', 'Body 2', 'A frameless display, a warm metal body\rand a design that fits the way you move.', 'Inter-Regular', 34, 50, 0, (255, 255, 255), 78),
    ('foottext', 'Footer text', 'EXPERIENCE NOVA — NOW ON DISPLAY', 'Inter-SemiBold', 26, 0, 300, (255, 255, 255), 100),
]


def build_jsx(path, targets):
    js = lambda v: json.dumps(v, ensure_ascii=True)
    L = ['// TEKTON NOVA - live type layers. Open tekton_nova_screen.psd, then File > Scripts > Browse... > this file.',
         '// Adds the group "COPY (live text)" at the same positions as the raster preview and hides the preview.',
         '// If Inter is not installed, Photoshop substitutes a font: select the group and change the font.',
         '#target photoshop', '(function () {',
         'if (!app.documents.length) { alert("Open tekton_nova_screen.psd first."); return; }',
         'var doc = app.activeDocument;',
         'var ru = app.preferences.rulerUnits, tu = app.preferences.typeUnits;',
         'app.preferences.rulerUnits = Units.PIXELS; app.preferences.typeUnits = TypeUnits.PIXELS;',
         'var set = doc.layerSets.add(); set.name = "COPY (live text)";',
         'function px(v) { return v.as ? v.as("px") : v; }',
         'function add(name, txt, font, size, leading, tracking, rgb, opacity, box) {',
         '  var l = set.artLayers.add(); l.kind = LayerKind.TEXT; l.name = name;',
         '  var t = l.textItem; t.contents = txt;',
         '  try { t.font = font; } catch (e) {}',
         '  t.size = new UnitValue(size, "px");',
         '  if (leading > 0) { t.useAutoLeading = false; t.leading = new UnitValue(leading, "px"); }',
         '  t.tracking = tracking;',
         '  var c = new SolidColor(); c.rgb.red = rgb[0]; c.rgb.green = rgb[1]; c.rgb.blue = rgb[2]; t.color = c;',
         '  t.position = [new UnitValue(box[0], "px"), new UnitValue(box[1] + size, "px")];',
         '  l.opacity = opacity;',
         '  var b = l.bounds; l.translate(new UnitValue(box[0] - px(b[0]), "px"), new UnitValue(box[1] - px(b[1]), "px"));',
         '}']
    for key, name, txt, font, size, lead, tr, rgb, op in TEXT:
        b = targets[key]
        L.append(f'add({js(name)}, {js(txt)}, {js(font)}, {size}, {lead}, {tr}, {list(rgb)}, {op}, [{b["l"]}, {b["t"]}]);')
    L += ['try { doc.layerSets.getByName("COPY (raster preview)").visible = false; } catch (e) {}',
          'app.preferences.rulerUnits = ru; app.preferences.typeUnits = tu;', '})();']
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


def main():
    os.makedirs(OUTD, exist_ok=True)
    base, group, targets = build_layers()
    layers = base + [dict(name='</Layer group>', section=3)] + group + [dict(name='COPY (raster preview)', section=1)]
    merged = Image.open(os.path.join(DOC, 'screen_draft.jpg')).convert('RGB')
    assert merged.size == (W, H), merged.size
    psd = os.path.join(OUTD, 'tekton_nova_screen.psd')
    write_psd(psd, layers, merged)
    build_jsx(os.path.join(OUTD, 'live_text.jsx'), targets)
    z = os.path.join(DOC, 'tekton_nova_screen_photoshop.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zz:
        zz.write(psd, 'tekton_nova_screen/tekton_nova_screen.psd')
        zz.write(os.path.join(OUTD, 'live_text.jsx'), 'tekton_nova_screen/live_text.jsx')
        zz.write(os.path.join(DOC, 'screen_draft.jpg'), 'tekton_nova_screen/preview.jpg')
    print('ok', os.path.relpath(psd, REPO), os.path.getsize(psd) // 1024, 'KB')


if __name__ == '__main__':
    main()
