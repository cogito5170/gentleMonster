"""한 쪽을 층이 나뉜 포토샵 파일로 (315 × 195mm · 300dpi · RGB) — 쪽 모듈의 layers() 를 층마다 굽는다.

  python3 tools/jaju_layout/psd_page.py <모듈>      예) p09_back_zine  ->  docs/jaju_rounding_vmd/photoshop/<모듈>.psd

모듈은 W · H · TMP · CSS · layers() [(이름, html, 보임) …, 아래에서 위로] 를 가진다(p11_zine · p09_back_zine).
층마다 같은 HTML 을 배경 없이 굽고(layer_shots.mjs) psd_write.py 가 PackBits 로 쓴다. 글은 그림 층(포토샵 글자 층이 아님).
"""
import importlib
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, '../..'))

from psd_write import write_psd  # noqa: E402

DPI = 300
OUTDIR = os.path.join(REPO, 'docs/jaju_rounding_vmd/photoshop')
SHOTS = os.path.join(REPO, 'tools/p1_layout/layer_shots.mjs')


def build(name):
    z = importlib.import_module(name)
    os.makedirs(z.TMP, exist_ok=True)
    os.makedirs(OUTDIR, exist_ok=True)
    ls = z.layers()
    h = os.path.join(z.TMP, f'{name}_layers.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>{name} layers</title><style>{z.CSS}"
                "html,body{background:transparent}.sheet{background:transparent!important;margin-bottom:12mm}</style></head><body>"
                + ''.join(f"<div class='sheet'>{html}</div>" for _, html, _ in ls) + "</body></html>")
    prefix = os.path.join(z.TMP, f'{name}_layer')
    subprocess.run(['node', SHOTS, h, prefix, str(DPI)], check=True)
    PW, PH = round(z.W / 25.4 * DPI), round(z.H / 25.4 * DPI)
    layers, comp = [], Image.new('RGBA', (PW, PH), (255, 255, 255, 255))
    for i, (lname, _, vis) in enumerate(ls):
        im = Image.open(f'{prefix}_{i + 1}.png').convert('RGBA').crop((0, 0, PW, PH))
        layers.append((lname, im, vis))
        if vis:
            comp.alpha_composite(im)
    out = os.path.join(OUTDIR, f'{name}.psd')
    n = write_psd(out, PW, PH, layers, comp.convert('RGB'), DPI)
    comp.convert('RGB').save(os.path.join(z.TMP, f'{name}_psd_composite.png'))
    print('wrote', out, n, 'layers', f'{PW}x{PH}px', f'{os.path.getsize(out) / 1e6:.1f} MB')
    return out


if __name__ == '__main__':
    build(sys.argv[1])
