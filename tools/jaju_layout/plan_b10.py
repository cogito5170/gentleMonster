"""JAJU 포트폴리오 — B10: B9 의 흐름(쪽 순서)은 그대로, 사례 1(ETÉREO) 재분석의 부족한 점을 지면 안에서 고친 판.

  python3 tools/jaju_layout/plan_b10.py   ->  docs/jaju_rounding_vmd/layout/plan_b10.pdf

사용자: "분석을 바탕으로 부족한 점을 보완하라. 임의 판단하에 수정. 단, 기존 B9 의 흐름의 순서는 유지하라."
분석: docs/jaju_rounding_vmd/ref_case1_etereo_b9.md. 쪽별 수정: docs/jaju_rounding_vmd/plan_b10.md
  03 Where people stop  색 · 시간 대신 사람 — 사람이 있는 컷 6장, 칸을 비운 엇갈린 격자, 캡션 = 이름 + 줄표 + 행동 한 줄  (#1 #2 #5 #7)
  04 · 05 · 07          제목을 쪽 제목 크기(32pt) 두 줄로, 아래 글을 그만큼 내림                                        (#8)
  08 A room             전면 사진 위의 기준선 · 십자를 뺌 (파트 대표 쪽의 뷰파인더는 사용자 결정이라 그대로)            (#6)
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b9 as b9  # noqa: E402

b8, b7, b6, b5, b4, b3, pe = b9.b8, b9.b7, b9.b7.b6, b9.b5, b9.b8.b4, b9.b8.b3, b9.pe
pc, t, div, photo, e = pe.pc, pe.t, pe.div, pe.photo, pe.e
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT


def move(html, x, y0, y1):
    """left:x · top:y0 인 칸을 top:y1 로."""
    a, b = f"left:{x}mm;top:{y0}mm;", f"left:{x}mm;top:{y1}mm;"
    assert a in html, a
    return html.replace(a, b, 1)


def big_title(html, old, new, x=14, y=22, w=84):
    """19pt 한 줄 제목(h2)을 32pt 두 줄 제목(h1)으로."""
    a = t(x, y, w, 10, old, 'h2')
    assert a in html, old
    return html.replace(a, t(x, 20, w + 10, 26, new, 'h1'), 1)


# ── 03 · Where people stop — 사람이 멈춘 자리 ─────────────────────────────────────────
PEOPLE = [  # pid, (행, 열), 초점, 이름, 행동 한 줄 — 사진에 보이는 것만 적는다
    ('PH-06', (0, 0), (0.35, 0.5), 'Food truck', '주문하기 전, 메뉴판 사진 앞에서 먼저 멈춘다.'),
    ('PH-11', (0, 1), (0.6, 0.5), 'Alley', '누군가는 지나가고, 누군가는 계단에 앉아 쉰다.'),
    ('PH-17', (1, 1), (0.55, 0.55), 'Breakwater', '접힌 파라솔 아래, 한 사람이 바다를 보고 앉았다.'),
    ('PH-04', (1, 2), (0.6, 0.55), 'Snack stand', '여럿이 같은 메뉴판을 함께 올려다본다.'),
    ('PH-01', (2, 0), (0.6, 0.6), 'Beach', '사람들은 물이 얕은 곳에 모여 선다.'),
    ('PH-03', (2, 2), (0.3, 0.55), 'Canoe', '해가 지는 쪽으로, 같은 박자로 노를 젓는다.'),
]


def p_grid():
    gx, gy, cw, gap = 100, 22, 59.5, 4.25
    ch = cw * 9 / 16
    o = [t(14, 20, 84, 26, 'Where people<br>stop.', 'h1'),
         t(14, 50, 84, 30, '<p>눈여겨보면 보인다.</p><p>사람들은 무언가 앞에서 걸음을 늦추고,</p><p>같은 곳을 함께 바라본다.</p>', 'kb'),
         t(14, 78, 80, 14, 'Look closely, and you see where people slow down — and what they look at together.', 'enb wrap'),
         t(14, 150, 84, 30, '<p>메뉴판 앞, 계단, 그늘 아래 —</p><p>사람이 멈춘 자리는</p><p>진열이 놓일 자리다.</p>', 'kbb'),
         t(14, 182, 84, 4, '17 FRAMES · 06 SHOWN', 'data')]
    for i, (pid, (r, c), f, name, act) in enumerate(PEOPLE):
        x, y = gx + c * (cw + gap), gy + r * (ch + 22)
        o.append(photo(pid, x, y, cw, ch, focus=f))
        o.append(t(x, y + ch + 2, cw, 12, f"<p><b>{name}–</b> {act}</p><p class='n'>N°{i + 1:02d}&nbsp;&nbsp;{pid}</p>", 'cap'))
    return ''.join(o)


# ── 04 · 05 · 07 — 제목을 크게 ───────────────────────────────────────────────────────
def p_detail():
    html = big_title(b4.p_detail(), 'What made me stop', 'What made<br>me stop.')
    return move(move(html, 14, 36, 50), 14, 60, 70)


def p_reading():
    html = big_title(b6.p_reading(), 'Reading a window', 'Reading<br>a window.')
    return move(move(html, 14, 36, 50), 14, 70, 76)


def p_collage():
    html = big_title(pe.p_collage(), 'From the city to the room', 'From the city<br>to the room.', w=126)
    return move(html, 14, 36, 47)


SWAP = {pe.p_grid: p_grid, b4.p_detail: p_detail, b6.p_reading: p_reading, pe.p_collage: p_collage}
PAGES = [(SWAP.get(p, p), g) for p, g in b9.PAGES]
b9.PAGES = b8.PAGES = b7.PAGES = b6.PAGES = PAGES
FULL = {8}  # 파트 대표 쪽이 아닌 전면 사진 쪽 — 사례 1 처럼 사진 위에 선을 얹지 않는다


def page(i, p, g):
    html, g = b7.page(i, p, g)
    if i in FULL:
        grid = b7.grid(True)
        assert grid in html
        html = html.replace(grid, '', 1)
    return html, g


CSS = b8.CSS + """
.cap{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:7pt;line-height:10.5pt;color:#9A8F82;word-break:keep-all}.cap p{white-space:normal}
.cap b{font-family:Lora,serif;font-weight:700;font-size:7.6pt;color:#EFE7DA}
.cap .n{font-family:Mono,monospace;font-size:5pt;letter-spacing:.08em;color:#6f665c;margin-top:.8mm}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for i, (p, g) in enumerate(PAGES):
        html, g = page(i, p, g)
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    h = os.path.join(TMP, 'plan_b10.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B10</title><style>{CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b10.pdf'), os.path.join(TMP, 'plan_b10')], check=True)


if __name__ == '__main__':
    main()
