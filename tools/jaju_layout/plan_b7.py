"""JAJU 포트폴리오 — B7: B6 의 흐름(쪽 순서)은 그대로, 사례 7(GUAVIARI SANS)에서 배운 레이아웃 · 텍스트 · 배치만 들인 판.

  python3 tools/jaju_layout/plan_b7.py   ->  docs/jaju_rounding_vmd/layout/plan_b7.pdf

사용자: "기존 B6 의 흐름 순서는 지켜라. 주어진 틀 안에서 레이아웃, 텍스트, 배치 등의 피드백을 진행한 후 수정."
분석 · 비교: docs/jaju_rounding_vmd/ref_case7_guaviari.md. B6 에서 바꾼 것:
  모든 쪽     네 모서리 표시(뷰파인더처럼) + 바닥 줄 세 칸(책 · 쪽 이름 · 번호) — 사례 7 의 격자를 모서리만
  사진 톤     파트 1 에만 하던 보정을 본문 전체(02–15)에 — 사례 7 은 모든 사진이 한 톤
  01 Prologue 아래에 세 파트를 한 줄로(/01 · /02 · /03 + 쪽) — 사례 7 영상 위의 TUKANO ✦ JIW ✦ NUKAK
  12 Breakdown 사진 위 바닥 줄을 밝게
  13 Proposal 칸 아래 '출처' 띠 — 칸이 어느 쪽에서 왔는지 (사례 7 의 바위 그림 A 를 상자에 넣고 글자를 양옆에)
  14 Often    '자주'를 큰 낱말 하나로 — 사례 7 의 INDESCIFRABLE
  뒤표지      Thank you 아래 크레디트 한 줄 — 사례 7 끝의 TORNUS · 크레디트
"""
import os
import re
import subprocess
import sys

from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b6 as b6  # noqa: E402

b5, b4, b3, pe = b6.b5, b6.b4, b6.b3, b6.pe
pc, t, div, photo, e, af, frame = pe.pc, pe.t, pe.div, pe.photo, pe.e, pe.af, pe.frame
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT
NAME = pe.NAME


# ── 사진 톤: 잘라 쓰는 작은 사본(b4.crop)에도 같은 보정 ───────────────────────────────────
_crop = b4.crop


def graded_crop(pid, x, y, w, h, cx, cy, span, marks=None):
    html = _crop(pid, x, y, w, h, cx, cy, span, marks)
    if not b4.GRADE['on']:
        return html
    f = os.path.join(b4.CROPS, f'{pid}_{cx}_{cy}_{span}.jpg')
    g = f[:-4] + '_g1.jpg'
    im = ImageEnhance.Color(Image.open(f).convert('RGB')).enhance(0.82)
    Image.blend(im, Image.new('RGB', im.size, (226, 196, 160)), 0.07).save(g, quality=84)
    return html.replace(f, g)


b4.crop = graded_crop


# ── 01 · Prologue — 아래에 세 파트를 한 줄로 ────────────────────────────────────────────
def p_prologue():
    html = b6.p_prologue().replace(div(14, 142, 5, 5, '', 'dotor'), '')
    cells = [('/01', 'Observe.', '관찰하다 — 사진', '02'), ('/02', 'Contain.', '담다 — 건축', '06'), ('/03', 'Fill.', '채우다 — 패션', '09')]
    o = []
    for i, (n, w, k, p) in enumerate(cells):
        x = 14 + i * 46
        o.append(t(x, 160, 42, 26, f"<p class='tn'>{n}</p><p class='tw'>{w}</p><p class='tk'>{k}&nbsp;&nbsp;·&nbsp;&nbsp;p.{p}</p>", 'tri'))
    g = ''.join(corner(14 + i * 46, 157, 1, 1, 2.6) for i in range(3))  # 칸마다 왼쪽 위 모서리만
    return html + ''.join(o) + svg(g)


# ── 13 · Proposal — 칸 아래 '출처' 띠 ──────────────────────────────────────────────────
def p_proposal():
    html = b4.p_proposal().replace(">Proposal</div>", ">Proposal.</div>", 1)
    src = [('FA-04', (888, 610), 360, 'a) EYE LEVEL', '← 05 Reading'), ('AR-07', (548, 420), 520, 'b) FRAME · LIGHT', '← 08 A room'),
           ('FA-04', (640, 930), 520, 'c) OUTFIT', '← 12 Breakdown')]
    o, g = [t(160, 158, 60, 4, 'SOURCE — 칸이 온 자리', 'data')], ''
    for i, (pid, (cx, cy), span, a, b) in enumerate(src):
        x = 160 + i * 38
        o.append(b4.crop(pid, x + 3, 164, 32, 20, cx, cy, span))
        o.append(t(x + 3, 186, 34, 8, f'<p>{a}</p><p>{b}</p>', 'data'))
        if i == 1:  # 가운데 칸(눈높이 · 조합)의 틀 — 사례 7 이 바위 그림을 상자에 넣듯
            g += f"<rect x='{x + 1.5}' y='162.5' width='35' height='23' class='bx'/>"
            g += ''.join(cross(px, py, 1.4) for px in (x + 1.5, x + 36.5) for py in (162.5, 185.5))
    return html + ''.join(o) + svg(g)


# ── 14 · Often — '자주'를 큰 낱말 하나로 ─────────────────────────────────────────────────
def p_often():
    row = [('COVER', (0.76, 0.45), 'FROM THE INSIDE'), ('PH-04', (0.6, 0.5), 'OBSERVE'), ('AR-03', (0.6, 0.5), 'CONTAIN'),
           ('AR-07', (0.5, 0.55), 'A ROOM'), ('FA-02', (0.45, 0.45), 'FILL')]
    o = []
    for i, (pid, f, w) in enumerate(row):
        x = 14 + i * 54.6
        o.append(photo(pid, x, 20, 50.6, 60, focus=f))
        o.append(t(x, 82, 50.6, 5, f"N°{i + 1:02d}&nbsp;&nbsp;{w}", 'data'))
    o += [t(14, 94, 270, 14, '자주 보고, 자주 담고, <span class=\'acc2\'>자주</span> 채운다.', 'pull3'),
          t(14, 110, 128, 30, '<p>JAJU 는 “자주 쓸수록, 최상의 삶”이라고 말한다. 진열도 자주 볼수록 정확해진다. '
                              '나는 매장을 돌며 자주 보고, 그 자리에 맞게 담고, 손님의 하루에 맞는 조합으로 채우는 VMD 가 되려 한다.</p>', 'prose'),
          t(156.5, 110, 128, 30, '<p>JAJU says, “the more often you use it, the better life becomes.” A display, too, becomes more precise the more often it is looked at. '
                                 'I want to be a VMD who looks often, holds each place as it is, and fills it with what fits the day.</p>', 'enb wrap'),
          t(10, 132, 290, 70, "Often<span class='acc2'>.</span>", 'giant')]
    return ''.join(o)


# ── 뒤표지 — Thank you 아래 크레디트 한 줄 ───────────────────────────────────────────────
def p_back():
    cr = ' &nbsp;+&nbsp; '.join([f'PHOTOGRAPHY — {NAME}', f'ARCHITECTURE MODELS — {NAME} (과제명 · 연도 ____)', f'STYLING — {NAME}',
                                 'TYPE — Young Serif · Lora · IBM Plex Mono', 'COVER IMAGE — ____'])
    return b5.p_back() + t(14, 196, 269, 4, cr, 'credit')


# ── 격자: 기준선 두 줄(위 · 아래) + 십자 + 바닥 줄 가운데 칸 ───────────────────────────────
def cross(x, y, r=1.8):
    return f"<line x1='{x - r}' y1='{y}' x2='{x + r}' y2='{y}' class='gx'/><line x1='{x}' y1='{y - r}' x2='{x}' y2='{y + r}' class='gx'/>"


def svg(g, cls=''):
    return div(0, 0, 297, 210, f"<svg class='ov grid {cls}' viewBox='0 0 297 210'>{g}</svg>", '')


def corner(x, y, dx, dy, r=4):
    return f"<polyline points='{x + dx * r},{y} {x},{y} {x},{y + dy * r}' class='gc'/>"


def grid(light):
    """판의 네 모서리만 — 뷰파인더처럼 (사용자: 위 · 아래 선 대신 모서리만)."""
    g = corner(14, 12, 1, 1) + corner(283, 12, -1, 1) + corner(14, 195, 1, -1) + corner(283, 195, -1, -1)
    return svg(g, 'lt' if light else '')


NAMES = {1: 'PROLOGUE', 2: 'OBSERVE', 3: 'WHERE PEOPLE STOP', 4: 'WHAT MADE ME STOP', 5: 'READING A WINDOW', 6: 'CONTAIN',
         7: 'CITY TO ROOM', 8: 'A ROOM', 9: 'FILL', 10: 'FOUR PLACES', 11: 'ITEMS', 12: 'BREAKDOWN', 13: 'PROPOSAL', 14: 'OFTEN',
         15: 'ABOUT'}
LIGHT = {2, 8, 9}  # 사진이 쪽 전체에 깔린 쪽
SWAP = {b6.p_prologue: p_prologue, b4.p_proposal: p_proposal, pe.p_often: p_often, b5.p_back: p_back}
PAGES = [(SWAP.get(p, p), g) for p, g in b6.PAGES]
b6.PAGES = PAGES  # b6.page() 가 PAGES 길이로 끝 쪽을 가린다


def page(i, p, g):
    if 1 < i < len(PAGES) - 1:
        g = 'g1'  # 보정을 본문 전체에
    html = b6.page(i, p, g)
    if i == 12:  # Breakdown — 바닥 줄 왼쪽이 사진 위에 놓인다
        html = html.replace("class='t ft'", "class='t ft lt'", 1)
    if 0 < i < len(PAGES) - 1:
        lt = i in LIGHT
        html += grid(lt) + t(98.5, 199, 100, 4, NAMES[i], 'ft c' + (' lt' if lt else ''))
    return html, g


CSS = b5.CSS + """
.ov.grid .gr{stroke:rgba(239,231,218,.16);stroke-width:.15}.ov.grid .gx{stroke:rgba(239,231,218,.55);stroke-width:.2}
.ov.grid.lt .gr{stroke:rgba(239,231,218,.4)}
.ov.grid .gc{fill:none;stroke:rgba(239,231,218,.6);stroke-width:.25}.ov.grid.lt .gc{stroke:rgba(239,231,218,.9)}.ov.grid.lt .gx{stroke:rgba(239,231,218,.85)}
.ov.grid .bx{fill:none;stroke:#D9773A;stroke-width:.25}
.tri .tn{font-family:Lora,serif;font-style:italic;font-size:10pt;color:#D9773A}
.tri .tw{font-family:Young,serif;font-size:15pt;line-height:19pt;color:#EFE7DA}
.tri .tk{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:7pt;color:#9A8F82}
.giant{font-family:Young,serif;font-size:205pt;line-height:205pt;color:#EFE7DA;white-space:nowrap;letter-spacing:-.01em}
.credit{font-family:Mono,monospace;font-size:4.6pt;letter-spacing:.08em;color:#9A8F82;white-space:nowrap}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for i, (p, g) in enumerate(PAGES):
        html, g = page(i, p, g)
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    h = os.path.join(TMP, 'plan_b7.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B7</title><style>{CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b7.pdf'), os.path.join(TMP, 'plan_b7')], check=True)


if __name__ == '__main__':
    main()
