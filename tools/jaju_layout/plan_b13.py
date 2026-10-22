"""JAJU 포트폴리오 — B13: B12 그대로, 03 쪽을 2-2 세션(스토리)에서 확정한 '안 A + 짧은 질문 하나'로 바꾸고, 04 의 겹치는 사진을 정리한 판.

  python3 tools/jaju_layout/plan_b13.py   ->  docs/jaju_rounding_vmd/layout/plan_b13.pdf

사용자: "2-2 의 변경된 스토리를 반영하여 수정하라."
2-2 세션 확정(claude/awesome-keller-otac19 09f64c3 · p03_thoughts_options.md 3안 · p03_story_options.md 안 A):
  03  제목 Where people stop. 그대로.
      본문  멈춘 사람은 대개 짧은 질문 하나를 하고 있다. 조금 더 있을까? 뭐 먹지? 어느 게 맛있어 보이지?
      맺음  나도 가게 앞에서 질문 하나를 한다. 어떻게 놓으면 지나가던 사람이 걸음을 멈출까.
      사진  2열 × 3줄(89.5 × 46.5mm), 사람마다 점선 틀, 바다 → 거리 → 가게. 캡션 = N° · 자리 · 질문(짐작) · 잰 HEX.
      데이터 17 FRAMES / 06 SHOWN · SIX PLACES, SIX QUESTIONS — MY GUESS. 시간대 글자는 뺀다.
  04  03 에 PH-07(불판 앞)이 들어와 겹치므로 d) Through the rail(PH-07) → d) Sprout(PH-10, 아직 안 쓴 사진).
      b) Pink 는 PH-01 을 크게 잘라 낸 한 사람이라 그대로 둔다(같은 장면의 세부 — 03 은 넓게, 04 는 한 점).
"""
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b12 as b12  # noqa: E402

b10 = b12.b10
b4, pe = b10.b4, b10.pe
pc, t, div, photo, af, frame = pe.pc, pe.t, pe.div, pe.photo, pe.af, pe.frame
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT


# ── 03 · Where people stop. — 안 A + 짧은 질문 하나 ──────────────────────────────────
A = [  # pid, 자리, 점선 틀 이름, 질문(짐작), 점선 틀(원본 비율 x, y, w, h) — 2-2 세션 p03_options.py 의 값
    ('PH-01', '얕은 물', 'IN SHALLOW WATER', '조금 더 있을까?', (0.42, 0.52, 0.12, 0.16)),
    ('PH-17', '파라솔 옆', 'BY A PARASOL', '어디가 제일 잘 보이지?', (0.27, 0.53, 0.17, 0.2)),
    ('PH-11', '가게 계단', 'ON A SHOP STEP', '잠깐 앉을까?', (0.47, 0.28, 0.2, 0.58)),
    ('PH-07', '불판 앞', 'AT THE GRILL', '다 익었나?', (0.16, 0.02, 0.36, 0.9)),
    ('PH-04', '간판 앞', 'UNDER THE SIGN', '뭐 먹지?', (0.44, 0.56, 0.32, 0.43)),
    ('PH-06', '메뉴판 앞', 'BEFORE THE MENU', '어느 게 맛있어 보이지?', (0.22, 0.32, 0.18, 0.66)),
]


def dashed(pid, box, label):
    W, H = Image.open(pc.path(pid)).size

    def m(to, s):
        fx, fy, fw, fh = box
        x0, y0 = to(fx * W, fy * H)
        r = f"x='{x0:.2f}' y='{y0:.2f}' width='{fw * W * s:.2f}' height='{fh * H * s:.2f}'"
        return (f"<rect {r} class='dshs'/><rect {r} class='dsh'/>"
                f"<text x='{x0 + .6:.2f}' y='{max(y0 - 1.1, 2.6):.2f}' class='afs'>{label}</text>")
    return m


def p_grid():
    gx, gy, cw, ch, gap = 100, 22, 89.5, 46.5, 4
    o = [t(14, 20, 94, 26, 'Where people<br>stop.', 'h1'),
         t(14, 50, 84, 34, '<p>멈춘 사람은 대개</p><p>짧은 질문 하나를 하고 있다.</p><p>조금 더 있을까? 뭐 먹지?</p><p>어느 게 맛있어 보이지?</p>', 'kb'),
         t(14, 86, 80, 18, 'People who stop are usually asking one short question. Stay a little longer? What should I eat? Which one looks good?', 'enb wrap'),
         t(14, 132, 84, 26, '<p>나도 가게 앞에서 질문 하나를 한다.</p><p>어떻게 놓으면</p><p>지나가던 사람이 걸음을 멈출까.</p>', 'kbb'),
         t(14, 160, 80, 14, 'In front of a shop, I ask one too: how should I place things so that people passing by will stop?', 'enb wrap'),
         t(14, 180, 84, 10, '<p>17 FRAMES / 06 SHOWN</p><p>SIX PLACES, SIX QUESTIONS — MY GUESS</p>', 'data')]
    for i, (pid, place, en, q, box) in enumerate(A):
        r, c = divmod(i, 2)
        x, y = gx + c * (cw + gap), gy + r * (ch + 10)
        hx = pe.accent(pid)
        o.append(photo(pid, x, y, cw, ch, marks=dashed(pid, box, en)))
        o.append(t(x, y + ch + 1.8, cw, 6, f"<p><span class='n3'>N°{i + 1:02d}</span><b>{place}–</b> {q}"
                                           f"<span class='sw3' style='background:{hx}'></span><span class='hx3'>{hx}</span></p>", 'cap'))
    return ''.join(o)


# ── 04 · What made me stop. — d) 를 PH-10 새싹으로 ──────────────────────────────────
def p_detail_raw():
    def chair(to, s):
        cx, cy = to(1072, 578)
        return af(cx, cy, 6.5, f'a)  {pe.accent("PH-05")}', 'left') + frame(6, 6, 166, 76, 'WIDE')

    def pink(to, s):
        return af(*to(687, 545), 4, 'b)')

    def sig(to, s):
        return af(*to(880, 94), 3.4, 'c)')

    def sprout(to, s):
        return af(*to(690, 290), 4.2, 'd)')

    keys = ''.join(f"<div class='k'><b>{a}</b> {b}<span>{c}</span></div>" for a, b, c in
                   [('a)', 'Red chair', '파란 바다, 모서리의 빨강'), ('b)', 'Pink', '수십 명 가운데 한 사람'),
                    ('c)', 'Signal', '어둠 속 빨간 신호'), ('d)', 'Sprout', '마른 잎 사이, 초록 싹 하나')])
    return ''.join([
        t(14, 22, 84, 10, 'What made me stop', 'h2'),
        t(14, 36, 84, 30, '<p>넓은 장면에서도 눈은 한 점에 먼저 간다.</p>', 'kb'),
        t(14, 60, 84, 60, keys, 'keys'),
        t(14, 150, 84, 30, '<p>진열도 같다.</p><p>시선이 먼저 닿을 한 점을 정하고,</p><p>그 점이 놓일 자리를 만든다.</p>', 'kbb'),
        photo('PH-05', 109, 22, 178, 100, focus=(0.5, 0.5), marks=chair),
        photo('PH-01', 109, 128, 57, 50, focus=(0.458, 0.64), zoom=3.0, marks=pink),
        photo('PH-08', 169.5, 128, 57, 50, focus=(0.6, 0.2), zoom=1.6, marks=sig),
        photo('PH-10', 230, 128, 57, 50, focus=(0.46, 0.4), zoom=1.4, marks=sprout),
        b4.RAW(4, 'PART 1 OBSERVE'),
    ])


def p_detail():
    html = b10.big_title(p_detail_raw(), 'What made me stop', 'What made<br>me stop.')
    return b10.move(b10.move(html, 14, 36, 50), 14, 60, 70)


PAGES = [({b10.p_grid: p_grid, b10.p_detail: p_detail}.get(p, p), g) for p, g in b10.PAGES]
b10.PAGES = b10.b9.PAGES = b10.b8.PAGES = b10.b7.PAGES = b10.b6.PAGES = PAGES

CSS = b10.CSS + """
.ov .dshs{fill:none;stroke:rgba(21,18,15,.55);stroke-width:.9}
.ov .dsh{fill:none;stroke:#EFE7DA;stroke-width:.35;stroke-dasharray:1.4 .9}
.cap .n3{font-family:Mono,monospace;font-size:5.6pt;letter-spacing:.06em;color:#6f665c;margin-right:1.6mm}
.cap .sw3{display:inline-block;width:2.2mm;height:2.2mm;margin:0 1mm 0 2mm;vertical-align:-.3mm}
.cap .hx3{font-family:Mono,monospace;font-size:5.6pt;color:#9A8F82}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for i, (p, g) in enumerate(PAGES):
        html, g = b10.page(i, p, g)
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    h = os.path.join(TMP, 'plan_b13.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B13</title><style>{CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b13.pdf'), os.path.join(TMP, 'plan_b13')], check=True)


if __name__ == '__main__':
    main()
