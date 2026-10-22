"""JAJU 포트폴리오 4쪽(/01 Observe., 표지부터 센 번호 · B17) — InDesign 파일.

  python3 tools/jaju_layout/indd_p04.py

  docs/jaju_rounding_vmd/indesign/p04_observe/   (+ p04_observe.zip)
    p04_observe.idml   InDesign 문서 (파일 > 열기 → .indd 로 저장)
    p04_observe.jsx    같은 쪽을 InDesign 안에서 짓는 스크립트 (IDML 이 열리지 않을 때)
    p04_observe.pdf    기준 시안 — plan_b17.pdf 의 4쪽
    Links/PH-13_g1.jpg 사진 (지원자 PH-13, 장 1 보정판: 채도 0.82 · 따뜻한 색 7%)
    Document Fonts/    Young Serif · Lora · IBM Plex Mono (OFL). Pretendard 는 따로 설치

값은 plan_b17 의 4쪽(HTML · mm)과 같다. 사진은 재단 여유까지 덮도록 약 3% 키웠다(가운데 그대로).
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
W, H, BL, MM = base.W, base.H, base.BLEED, base.MM
IMG = os.path.join(base.REPO, 'out/jaju_layout/screen/PH-13_g1.jpg')  # plan_b17 이 만든 보정판
FILE = 'PH-13_g1.jpg'
PX = Image.open(IMG).size
YS, LO, P, MO = 'Young Serif', 'Lora', 'Pretendard', 'IBM Plex Mono'

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

# 사진: 시안은 left −38.333 · 폭 373.665 · 높이 210 → 재단 여유(216)까지 같은 가운데로 키움
s = (H + 2 * BL) / H
iw, cx = 373.665 * s, -38.333 + 373.665 / 2
items = [
    dict(kind='image', file=FILE, px=PX, place=(cx - iw / 2, -BL, iw, H + 2 * BL), name='photo PH-13', **FULL),
    dict(kind='rect', fill='Shade', name='shade (bottom)', feather=[(30, 0), (55, 25), (100, 78)], **FULL),
]


def ln(pts, color, wmm, op, name):
    return dict(kind='line', pts=pts, x1=pts[0][0], y1=pts[0][1], x2=pts[-1][0], y2=pts[-1][1],
                color=color, weight=wmm * MM, opacity=op, name=name)


items += [ln([(14, 12), (283, 12)], 'Grid Cream', .15, 40, 'rule top'), ln([(14, 195), (283, 195)], 'Grid Cream', .15, 40, 'rule bottom')]
for y in (12, 195):
    items += [ln([(146.7, y), (150.3, y)], 'Grid Cream', .2, 85, f'cross {y} h'), ln([(148.5, y - 1.8), (148.5, y + 1.8)], 'Grid Cream', .2, 85, f'cross {y} v')]
corners = [[(20, 12), (14, 12), (14, 18)], [(277, 12), (283, 12), (283, 18)], [(20, 195), (14, 195), (14, 189)], [(277, 195), (283, 195), (283, 189)]]
for i, c in enumerate(corners):
    items += [ln(c, 'Under', .9, 35, f'viewfinder {i + 1} under'), ln(c, 'Grid Cream', .3, 90, f'viewfinder {i + 1}')]
items += [
    T(14, 114, 200, 8, [('Part Num', '/01')], 'part number'),
    T(12.5, 126, 280, 48, [('Part Word', 'Observe.')], 'part word'),
    T(14, 172, 200, 8, [('Line KO', '가게 밖, 스쳐 지나가는 일상에서도 나는 사람들을 눈여겨본다.')], 'line ko'),
    T(14, 180, 200, 6, [('Line EN', 'Outside the shop, in everyday moments, I keep watching people.')], 'line en'),
    T(14, 199, 160, 4, [('Folio', 'FROM THE INSIDE  —  PART 1 OBSERVE')], 'folio left'),
    T(98.5, 199, 100, 4, [('Folio Center', 'OBSERVE')], 'folio center'),
    T(243, 199, 40, 4, [('Folio Right', '04')], 'folio number'),
]
base.ITEMS = items


def main():
    os.makedirs(os.path.join(DIR, 'Links'), exist_ok=True)
    os.makedirs(os.path.join(DIR, 'Document Fonts'), exist_ok=True)
    base.build_idml(os.path.join(DIR, NAME + '.idml'))
    base.build_jsx(os.path.join(DIR, NAME + '.jsx'))
    shutil.copyfile(IMG, os.path.join(DIR, 'Links', FILE))
    for f in ('YoungSerif-Regular.ttf', 'YoungSerif-OFL.txt', 'Lora-Italic.ttf', 'Lora-OFL.txt', 'IBMPlexMono-Regular.ttf', 'IBMPlexMono-OFL.txt'):
        shutil.copyfile(os.path.join(base.FONTS, f), os.path.join(DIR, 'Document Fonts', f))
    pdf = os.path.join(base.REPO, 'docs/jaju_rounding_vmd/layout/plan_b17.pdf')
    subprocess.run(['pdfseparate', '-f', '4', '-l', '4', pdf, os.path.join(DIR, NAME + '.pdf')], check=True)
    with zipfile.ZipFile(DIR + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(DIR):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(DIR)))
    print('wrote', DIR)


if __name__ == '__main__':
    main()
