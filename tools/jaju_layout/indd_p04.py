"""JAJU 포트폴리오 4쪽(/01 Observe., 표지부터 센 번호 · B17) — InDesign 파일, 판형 315 × 195 mm.

  python3 tools/jaju_layout/indd_p04.py

  docs/jaju_rounding_vmd/indesign/p04_observe/   (+ p04_observe.zip)
    p04_observe.idml   InDesign 문서 (파일 > 열기 → .indd 로 저장)
    p04_observe.jsx    같은 쪽을 InDesign 안에서 짓는 스크립트 (IDML 이 열리지 않을 때)
    p04_observe.pdf    기준 시안 — 같은 값으로 그린 315 × 195 한 쪽
    Links/PH-13_g1.jpg 사진 (지원자 PH-13, 장 1 보정판: 채도 0.82 · 따뜻한 색 7%)
    Document Fonts/    Young Serif · Lora · IBM Plex Mono (OFL). Pretendard 는 따로 설치

A4(297 × 210) 판의 4쪽을 315 × 195 로 옮겼다: 좌우 여백 14mm · 위 기준선 12mm · 아래 기준선 바닥에서 15mm 는 그대로,
아래에 붙은 글(/01 · Observe. · 두 줄)은 15mm 위로, 가운데 십자 · 바닥 가운데 글은 새 가운데(157.5mm)로. 사진은 높이 기준으로 재단 여유까지 꽉 채움.
사진 아래 어둡게 = 사각형(#140E08) + 그레이디언트 페더(위 30% 투명 → 55% 25% → 아래 78%).
격자: 위 · 아래 기준선(크림 40%) + 가운데 십자(85%) + 네 모서리 뷰파인더(크림 90% 0.3mm, 아래에 어두운 0.9mm 밑선).
"""
import os
import shutil
import subprocess
import sys
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import indd_p03 as base  # noqa: E402

NAME = 'p04_observe'
DIR = os.path.join(base.REPO, 'docs/jaju_rounding_vmd/indesign', NAME)
# 판형: 315 × 195 mm (사용자 2026-10-22 "화면 크기는 앞으로 315 x 195 로 맞추어 작업한다")
W, H = 315.0, 195.0
base.W, base.H = W, H
base.WP, base.HP = W * base.MM, H * base.MM
base.SPREAD_T = f'1 0 0 1 {-base.WP / 2:.4f} {-base.HP / 2:.4f}'
BL, MM = base.BLEED, base.MM
IMG = os.path.join(base.REPO, 'out/jaju_layout/screen/PH-13_g1.jpg')  # plan_b17 이 만든 보정판
FILE = 'PH-13_g1.jpg'
PX = Image.open(IMG).size
YS, LO, P, MO = 'Young Serif', 'Lora', 'Pretendard', 'IBM Plex Mono'
CX = W / 2               # 가운데 십자 · 가운데 바닥 글
TOP, BOT = 12, H - 15    # 위 · 아래 기준선 (A4 판의 12 · 195 와 같은 여백)
DY = BOT - 195           # A4 판에서 아래에 붙은 것들을 옮기는 양

base.PAGE_NO = 4
base.COLORS = {'Paper Cream': (246, 240, 230), 'Grid Cream': (239, 231, 218), 'Shade': (20, 14, 8), 'Under': (21, 18, 15)}
base.STYLES = {
    'Part Num':  dict(font=LO, style='Italic', size=20, lead=24, color='Paper Cream', align='left'),
    'Part Word': dict(font=YS, style='Regular', size=118, lead=118, color='Paper Cream', align='left'),
    'Line KO':   dict(font=P, style='Bold', size=13, lead=16, color='Paper Cream', align='left'),
    'Line EN':   dict(font=LO, style='Italic', size=9, lead=11, color='Paper Cream', align='left'),
    'Folio':        dict(font=MO, style='Regular', size=6, lead=8, color='Paper Cream', align='left', track=100),
    'Folio Center': dict(font=MO, style='Regular', size=6, lead=8, color='Paper Cream', align='center', track=100),
    'Folio Right':  dict(font=MO, style='Regular', size=6, lead=8, color='Paper Cream', align='right', track=100),
}
T, L = base.T, base.L
FULL = dict(x=-BL, y=-BL, w=W + 2 * BL, h=H + 2 * BL)

# 사진: 재단 여유까지 꽉 차게(높이 기준), 가운데 그대로
ih = H + 2 * BL
iw = PX[0] / PX[1] * ih
PLACE = (CX - iw / 2, -BL, iw, ih)
SHADE = [(30, 0), (55, 25), (100, 78)]
items = [
    dict(kind='image', file=FILE, px=PX, place=PLACE, name='photo PH-13', **FULL),
    dict(kind='rect', fill='Shade', name='shade (bottom)', feather=SHADE, **FULL),
]


def ln(pts, color, wmm, op, name):
    return dict(kind='line', pts=pts, x1=pts[0][0], y1=pts[0][1], x2=pts[-1][0], y2=pts[-1][1],
                color=color, weight=wmm * MM, opacity=op, name=name)


R = W - 14
items += [ln([(14, TOP), (R, TOP)], 'Grid Cream', .15, 40, 'rule top'), ln([(14, BOT), (R, BOT)], 'Grid Cream', .15, 40, 'rule bottom')]
for y in (TOP, BOT):
    items += [ln([(CX - 1.8, y), (CX + 1.8, y)], 'Grid Cream', .2, 85, f'cross {y} h'), ln([(CX, y - 1.8), (CX, y + 1.8)], 'Grid Cream', .2, 85, f'cross {y} v')]
CORNERS = [[(20, TOP), (14, TOP), (14, TOP + 6)], [(R - 6, TOP), (R, TOP), (R, TOP + 6)],
           [(20, BOT), (14, BOT), (14, BOT - 6)], [(R - 6, BOT), (R, BOT), (R, BOT - 6)]]
for i, c in enumerate(CORNERS):
    items += [ln(c, 'Under', .9, 35, f'viewfinder {i + 1} under'), ln(c, 'Grid Cream', .3, 90, f'viewfinder {i + 1}')]
TEXTS = [  # (x, y, w, h, style, 글, 이름) — y 는 A4 판에서 DY 만큼 위로
    (14, 114 + DY, 200, 8, 'Part Num', '/01', 'part number'),
    (12.5, 126 + DY, 290, 48, 'Part Word', 'Observe.', 'part word'),
    (14, 172 + DY, 220, 8, 'Line KO', '가게 밖, 스쳐 지나가는 일상에서도 나는 사람들을 눈여겨본다.', 'line ko'),
    (14, 180 + DY, 220, 6, 'Line EN', 'Outside the shop, in everyday moments, I keep watching people.', 'line en'),
    (14, BOT + 4, 160, 4, 'Folio', 'FROM THE INSIDE  —  PART 1 OBSERVE', 'folio left'),
    (CX - 50, BOT + 4, 100, 4, 'Folio Center', 'OBSERVE', 'folio center'),
    (R - 40, BOT + 4, 40, 4, 'Folio Right', '04', 'folio number'),
]
items += [T(x, y, w, h, [(st, s)], n) for x, y, w, h, st, s, n in TEXTS]
base.ITEMS = items


def reference_pdf(path_out):
    """같은 값으로 315 × 195 시안 PDF (Chromium)."""
    sys.path.insert(0, HERE)
    import plan_e as pe
    cls = {'Part Num': 'pt pn sl', 'Part Word': 'pt pw', 'Line KO': 'pt pk', 'Line EN': 'pt pe',
           'Folio': 'ft lt', 'Folio Center': 'ft lt c', 'Folio Right': 'ft lt r'}
    ox, oy, w2, h2 = PLACE
    g = ''.join(f"<polyline points='{' '.join(f'{a},{b}' for a, b in it['pts'])}' style='fill:none;stroke:{'#15120F' if it['color'] == 'Under' else '#EFE7DA'};"
                f"stroke-opacity:{it['opacity'] / 100};stroke-width:{it['weight'] / MM}'/>" for it in items if it['kind'] == 'line')
    body = (f"<div class='ph' style='left:0;top:0;width:{W}mm;height:{H}mm'><img src='file://{IMG}' style='left:{ox}mm;top:{oy}mm;width:{w2}mm;height:{h2}mm'></div>"
            f"<div style='left:0;top:0;width:{W}mm;height:{H}mm;background:linear-gradient(to top,rgba(20,14,8,.78),rgba(20,14,8,.25) 45%,rgba(20,14,8,0) 70%)'></div>"
            + ''.join(f"<div class='t {cls[st]}' style='left:{x}mm;top:{y + (6 if st == 'Part Num' else 0)}mm;width:{w}mm;height:{h}mm'>{s}</div>" for x, y, w, h, st, s, _ in TEXTS)
            + f"<div style='left:0;top:0;width:{W}mm;height:{H}mm'><svg class='ov' viewBox='0 0 {W} {H}'>{g}</svg></div>")
    css = pe.CSS + (f"@page{{size:{W}mm {H}mm;margin:0}}.sheet{{width:{W}mm;height:{H}mm;background:#15120F}}"
                    ".pn.sl{font-family:Lora,serif;font-style:italic;font-size:20pt;letter-spacing:0;margin-top:-6mm}")
    h = os.path.join(base.REPO, 'out/jaju_layout', NAME + '.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><style>{css}</style></head><body><div class='sheet'>{body}</div></body></html>")
    subprocess.run(['node', pe.PRINT, h, path_out, os.path.join(base.REPO, 'out/jaju_layout', NAME)], check=True)


def main():
    os.makedirs(os.path.join(DIR, 'Links'), exist_ok=True)
    os.makedirs(os.path.join(DIR, 'Document Fonts'), exist_ok=True)
    base.build_idml(os.path.join(DIR, NAME + '.idml'))
    base.build_jsx(os.path.join(DIR, NAME + '.jsx'))
    shutil.copyfile(IMG, os.path.join(DIR, 'Links', FILE))
    for f in ('YoungSerif-Regular.ttf', 'YoungSerif-OFL.txt', 'Lora-Italic.ttf', 'Lora-OFL.txt', 'IBMPlexMono-Regular.ttf', 'IBMPlexMono-OFL.txt'):
        shutil.copyfile(os.path.join(base.FONTS, f), os.path.join(DIR, 'Document Fonts', f))
    reference_pdf(os.path.join(DIR, NAME + '.pdf'))
    with zipfile.ZipFile(DIR + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(DIR):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(DIR)))
    print('wrote', DIR)


if __name__ == '__main__':
    main()
