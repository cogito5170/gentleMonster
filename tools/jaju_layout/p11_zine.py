"""JAJU 포트폴리오 11쪽 Four places, four outfits. — 사례 4(스케이트 진 PEACE. LOVE. SKATE.) 꼴로 다시 짠 판 (315 × 195).

  python3 tools/jaju_layout/p11_zine.py   ->  docs/jaju_rounding_vmd/layout/p11_zine.pdf

사용자: "기존 첫번째 이미지(사용자가 InDesign 에서 다듬은 Four places 쪽)의 페이지를 두번째 페이지(스케이트 진)의 레이아웃, 배치,
폰트 등을 참고하여 재가공하라. pdf로 보내라."
사례에서 가져온 것:
  · 살구색 종이 바탕 + 파랑 한 색으로 찍은 사진(그레이 → 파랑 두 톤, 망점) — 사진은 종이 위에 곱해져 흰 곳이 종이색이 된다
  · 쪽을 가로지르는 아주 좁고 굵은 빨간 대문자 낱말 셋, 마침표로 끝(PEACE. / LOVE. / SKATE.) — 왼쪽 가운데 · 오른쪽 위 · 오른쪽 아래
    → PLACE. / MATCH. / OUTFIT. (장소 · 맞추다 · 옷 — 파트 2 의 말). 쪽 제목 'Four places, four outfits.' 는 작은 줄로 둔다
  · 파랑 체크(픽셀) 띠: 세로 띠 · 가로 띠 · 흩어진 조각, 단색 파랑 막대
  · 사진은 겹치고 잘리며 쪽 끝까지 — 왼쪽은 큰 사진 하나, 오른쪽은 위 넓은 사진 + 아래 사진 (그 위로 낱말)
  · 손 낙서 · 찢은 종이 가장자리는 그림을 새로 그리는 일이라 넣지 않았다
글 · 값: 사용자 InDesign 쪽 그대로 — 리드 두 줄, N°01–04 캡션, PALETTE(#261F0A · #070A10 · #72727F · #6D6F71).
바닥 줄은 새 구성(파트 2 Match, 11쪽)으로.
좁은 굵은 글꼴이 없어 Instrument Sans Bold 장평 62%. InDesign 에서는 가진 좁은 고딕(예: 210 타임라인 Bold, Anton 류)으로 바꾸면 사례에 더 가깝다.
"""
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import part2_match as p2  # noqa: E402

d, W, H, FA, CROPS = p2.d, p2.W, p2.H, p2.FA, p2.CROPS
OUT, TMP, PRINT, FONTS = p2.OUT, p2.TMP, p2.PRINT, p2.FONTS
PAPER, INKB, RED, INK = '#E6A58C', '#2C5F86', '#E0352B', '#1B1B1A'
CX = 157.5

LEAD = ['나는 그날 갈 장소에 옷의 톤을 맞춘다.', '장소가 틀이라면, 옷은 그 틀을 채우는 조합이다.']
PALETTE = [('OLIVE PARKA', '#261F0A'), ('BLACK COAT', '#070A10'), ('BEIGE JACKET', '#72727F'), ('GREY KNIT', '#6D6F71')]


def _rgb(hx):
    return [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def duo(pid, x, y, w, h, cx, cy, span, bright=1.12):
    """사진을 파랑 한 색 + 망점으로 (사례의 리소 인쇄 꼴). 자르기는 part2_match.crop 과 같은 식.
    색은 파일에 구워 넣는다(InDesign 에서도 같게): 회색 → 대비 1.35 · 밝기 → 파랑과 '스크린' → 종이와 '곱하기',
    망점은 칸 0.85mm · 반지름 0.23칸의 파랑 점을 55% 로 곱한다 — 앞 판의 CSS 와 같은 식."""
    import numpy as np
    im = Image.open(os.path.join(FA, pid + '.jpg')).convert('L')
    IW, IH = im.size
    sh = span * h / w
    if sh > IH:
        span, sh = IH * w / h, IH
    lft, tp = max(0, min(IW - span, cx - span / 2)), max(0, min(IH - sh, cy - sh / 2))
    c = im.crop((int(lft), int(tp), int(lft + span), int(tp + sh)))
    c.thumbnail((1400, 1400))
    v = np.asarray(c, dtype=np.float32) / 255
    v = np.clip(((v - .5) * 1.35 + .5) * bright, 0, 1)[..., None]
    blue, paper = np.array(_rgb(INKB)), np.array(_rgb(PAPER))
    out = (1 - (1 - blue) * (1 - v)) * paper
    ppm = c.size[0] / w                                   # 픽셀 / mm
    cell = .85 * ppm
    yy, xx = np.mgrid[0:c.size[1], 0:c.size[0]]
    dx, dy = (xx % cell) - cell / 2, (yy % cell) - cell / 2
    dot = (np.hypot(dx, dy) < .23 * cell)[..., None]
    out = np.where(dot, out * (1 - .55 + .55 * blue), out)
    os.makedirs(CROPS, exist_ok=True)
    f = os.path.join(CROPS, f'zine_{pid}_{cx}_{cy}_{span:.0f}_{w:.0f}x{h:.0f}_duo.jpg')
    Image.fromarray((out * 255).astype('uint8'), 'RGB').save(f, quality=88)
    return d(x, y, w, h, f"<img src='file://{f}' style='position:absolute;left:0;top:0;width:{w}mm;height:{h}mm'>", 'duo')


def checker(x, y, cols, rows, cell=3.6, seed=1, density=.5):
    """체크(픽셀) 띠 — 칸마다 정해진 규칙(시드)으로 켜고 끈다. 같은 값이면 늘 같은 무늬."""
    r = ''
    for j in range(rows):
        for i in range(cols):
            v = ((i * 73856093) ^ (j * 19349663) ^ (seed * 83492791)) % 1000 / 1000
            if (i + j) % 2 == 0 and v < density + .25 or v < density * .4:
                r += f"<rect x='{x + i * cell:.2f}' y='{y + j * cell:.2f}' width='{cell:.2f}' height='{cell:.2f}'/>"
    return r


def layers():
    """쪽을 층으로 — 아래에서 위로 (이름, html, 보임). PDF · InDesign 은 모두 이어 붙이고, 포토샵 파일은 층마다 따로 굽는다."""
    blue = (checker(0, 0, 9, 14, seed=3, density=.45)            # 왼쪽 위 흩어진 체크
            + checker(106, 30, 4, 34, seed=7, density=.55)       # 왼쪽 쪽의 세로 띠
            + "<rect x='118' y='0' width='22' height='26'/>"      # 단색 막대(사례의 청록 막대)
            + checker(160, 66, 4, 31, seed=11, density=.55)      # 오른쪽 쪽의 세로 띠
            + checker(176, 104.6, 36, 2, seed=5, density=.6)     # 가로 띠
            + checker(268, 0, 13, 3, seed=9, density=.5))        # 오른쪽 위 조각
    sw = ''
    for i, (n, hx) in enumerate(PALETTE):
        x = 100 + i * 14
        sw += p2.sw(x, 166.5, hx, 12.6, 4.6) + d(x, 171.8, 14, 7, f'<p>{n.split()[0]}</p><p>{hx}</p>', 't zc s')
    return [
        ('종이', f"<svg class='ov' viewBox='0 0 {W} {H}'><rect x='0' y='0' width='{W}' height='{H}' fill='{PAPER}'/></svg>", True),
        # 왼쪽: 큰 사진(밤 강변) — 쪽 왼쪽 끝까지 / 오른쪽 위 넓은 사진(놀이공원) · 오른쪽 아래(바위) · 그 사이 좁은 사진(가게 앞)
        ('사진 N°01 밤 강변', duo('FA-01', 0, 8, 122, 150, 820, 1150, 1500, bright=1.9), True),
        ('사진 N°03 놀이공원', duo('FA-05', 176, 36, 139, 66, 640, 900, 1125), True),
        ('사진 N°04 바위', duo('FA-03', 214, 114, 91, 64.5, 560, 700, 900), True),
        ('사진 N°02 가게 앞', duo('FA-04', 160, 112, 46, 66.5, 640, 900, 640), True),
        ('체크 띠', f"<svg class='ov' viewBox='0 0 {W} {H}'><g fill='{INKB}' class='chk'>{blue}</g></svg>", True),
        # 빨간 낱말 셋 — 사례처럼 사진 · 체크 위를 가로지른다
        ('PLACE.', d(26, 62, 140, 40, '<p>PLACE.</p>', 't zw'), True),
        ('MATCH.', d(170, 4, 140, 40, '<p>MATCH.</p>', 't zw'), True),
        ('OUTFIT.', d(196, 140, 120, 40, '<p>OUTFIT.</p>', 't zw'), True),
        # 작은 글 — 제목 · 리드 · 캡션 · 팔레트 (사용자 쪽의 글)
        ('제목 · 리드', d(14, 160, 100, 5, '<p>FOUR PLACES, FOUR OUTFITS.</p>', 't zs')
         + d(14, 165.5, 120, 12, ''.join(f'<p>{s}</p>' for s in LEAD), 't zk'), True),
        ('캡션 N°01–04', d(3, 152, 60, 4, '<p>N°01&nbsp;&nbsp;NIGHT&nbsp;&nbsp;RIVERSIDE</p>', 't zc pa')
         + d(162.5, 173.5, 44, 4, '<p>N°02&nbsp;&nbsp;EVENING</p><p>SHOP FRONT</p>', 't zc pa')
         + d(178.5, 97.5, 80, 4, '<p>N°03&nbsp;&nbsp;AFTERNOON PARK</p>', 't zc pa')
         + d(216.5, 116.5, 80, 4, '<p>N°04&nbsp;&nbsp;SUNNY SEASIDE ROCKS</p>', 't zc pa'), True),
        ('팔레트', d(100, 161.6, 56, 4, '<p>PALETTE — 착장 사진에서 잰 색</p>', 't zc s') + sw, True),
        ('접는 선', f"<svg class='ov' viewBox='0 0 {W} {H}'>"
                  f"<line x1='{CX}' y1='0' x2='{CX}' y2='{H}' style='stroke:{INK};stroke-opacity:.12;stroke-width:.3'/></svg>", True),
        ('바닥 줄', p2.folio(11, 'FOUR PLACES'), True),
    ]


def page():
    return ''.join(h for _, h, _ in layers())


KO = p2.KO
CSS = p2.CSS + f"""
.duo{{overflow:hidden}}

.zw{{font-family:Inst,sans-serif;font-weight:700;font-size:118pt;line-height:110pt;letter-spacing:-.01em;color:{RED};
  transform:scaleX(.62);transform-origin:0 0}}
.zs{{font-family:Inst,sans-serif;font-weight:700;font-size:8pt;line-height:10pt;letter-spacing:.1em;color:{INK}}}
.zk{{font-family:{KO};font-size:9pt;line-height:13.5pt;color:{INK}}}
.zc{{font-family:Mono,monospace;font-size:6pt;line-height:7.6pt;letter-spacing:.06em;color:{INK};white-space:nowrap}}
.zc.s{{font-size:5.4pt;line-height:6.8pt}}.zc.pa{{color:#F7E7DC}}.zc p{{white-space:nowrap}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'p11_zine.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU p11 zine</title><style>{CSS}</style></head>"
                f"<body><div class='sheet' style='background:{PAPER}'>{page()}</div></body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'p11_zine.pdf'), os.path.join(TMP, 'p11z')], check=True)


if __name__ == '__main__':
    main()
