"""JAJU 포트폴리오 11쪽 Four places 진(zine) 판 — 포토샵 파일(층 나눔, 315 × 195mm · 300dpi · RGB).

  python3 tools/jaju_layout/psd_p11z.py   ->  docs/jaju_rounding_vmd/photoshop/p11_zine.psd

층(아래 → 위): 종이 · 사진 N°01–04 · 체크 띠 · PLACE. · MATCH. · OUTFIT. · 제목 · 리드 · 캡션 · 팔레트 · 접는 선 · 바닥 줄.
층마다 p11_zine.layers() 의 같은 HTML 을 배경 없이 300dpi 로 구워 넣는다(layer_shots.mjs) — PDF · InDesign 과 같은 자리 · 같은 색.
글은 그림 층이다(포토샵 글자 층이 아님) — 글을 고치려면 InDesign 파일(p11_zine.idml)에서.
"""
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, '../..'))

import p11_zine as z  # noqa: E402
from psd_write import write_psd  # noqa: E402

DPI = 300
OUTDIR = os.path.join(REPO, 'docs/jaju_rounding_vmd/photoshop')
SHOTS = os.path.join(REPO, 'tools/p1_layout/layer_shots.mjs')


def main():
    os.makedirs(z.TMP, exist_ok=True)
    os.makedirs(OUTDIR, exist_ok=True)
    ls = z.layers()
    h = os.path.join(z.TMP, 'p11_zine_layers.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU p11 zine layers</title><style>{z.CSS}"
                "html,body{background:transparent}.sheet{background:transparent!important;margin-bottom:12mm}</style></head><body>"
                + ''.join(f"<div class='sheet'>{html}</div>" for _, html, _ in ls) + "</body></html>")
    prefix = os.path.join(z.TMP, 'p11z_layer')
    subprocess.run(['node', SHOTS, h, prefix, str(DPI)], check=True)
    PW, PH = round(z.W / 25.4 * DPI), round(z.H / 25.4 * DPI)
    layers = []
    comp = Image.new('RGBA', (PW, PH), (255, 255, 255, 255))
    for i, (name, _, vis) in enumerate(ls):
        im = Image.open(f'{prefix}_{i + 1}.png').convert('RGBA').crop((0, 0, PW, PH))
        layers.append((name, im, vis))
        if vis:
            comp.alpha_composite(im)
    out = os.path.join(OUTDIR, 'p11_zine.psd')
    n = write_psd(out, PW, PH, layers, comp.convert('RGB'), DPI)
    comp.convert('RGB').save(os.path.join(z.TMP, 'p11z_psd_composite.png'))
    print('wrote', out, n, 'layers', f'{PW}x{PH}px', f'{os.path.getsize(out) / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
