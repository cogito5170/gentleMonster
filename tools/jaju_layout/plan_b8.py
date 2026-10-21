"""JAJU 포트폴리오 — B8: B7 의 흐름(쪽 순서)은 그대로, 사례 4(SKATE FASHION HISTORY 진)를 다시 보고 패션 파트의 제목 · 배치만 고친 판.

  python3 tools/jaju_layout/plan_b8.py   ->  docs/jaju_rounding_vmd/layout/plan_b8.pdf

사용자: "기존 B7 의 흐름 순서는 지켜라. 주어진 틀 안에서 레이아웃, 텍스트, 배치 등의 피드백을 진행한 후 수정."
분석 · 비교: docs/jaju_rounding_vmd/ref_case4_skate_b7.md. B7 에서 바꾼 것 (모두 파트 3):
  10 Four places  제목을 가운데 접는 선 양쪽으로 나눔 — 'Four places,' (사진 위) | 'four outfits.' (사례 4 의 ASPHALT | SURFERS)
  11 Items        제목을 쪽 제목 크기(32pt)로 — 사례 4 는 패션 쪽의 제목이 가장 크다
  12 Breakdown    질문 제목 'Front, or back?' — 사례 4 끝의 질문 → 지금 → 선언 (12 질문 · 13 Proposal 지금 · 14 Often 선언)
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b7 as b7  # noqa: E402

b6, b5, b4, b3, pe = b7.b6, b7.b5, b7.b4, b7.b3, b7.pe
pc, t, div, photo, e = pe.pc, pe.t, pe.div, pe.photo, pe.e
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT


# ── 10 · Four places — 제목을 접는 선 양쪽으로 ─────────────────────────────────────────
def p_four():
    html = b4.p_four().replace(t(162, 22, 122, 10, 'Four places, four outfits', 'h2'), '')
    return html + t(10, 20, 134, 14, 'Four places,', 'h1 r lt1') + t(162, 20, 122, 14, 'four outfits.', 'h1')


# ── 11 · Items — 제목을 크게 ──────────────────────────────────────────────────────────
def p_items():
    html = b4.p_items()
    html = html.replace(t(14, 22, 84, 10, 'Items', 'h2'), t(14, 20, 84, 14, 'Items.', 'h1'))
    html = html.replace(t(14, 36, 84, 40, '<p>조합은 아이템에서 시작한다.</p><p>자주 입는 여섯 가지를</p><p>진열하듯 하나씩 놓았다.</p>', 'kb'),
                        t(14, 40, 84, 40, '<p>조합은 아이템에서 시작한다.</p><p>자주 입는 여섯 가지를</p><p>진열하듯 하나씩 놓았다.</p>', 'kb'))
    return html.replace(t(14, 74, 82, 20, 'A combination starts from items. Six things I wear often, set out one by one.', 'enb wrap'),
                        t(14, 78, 82, 20, 'A combination starts from items. Six things I wear often, set out one by one.', 'enb wrap'))


# ── 12 · Breakdown — 질문 제목 ────────────────────────────────────────────────────────
def p_breakdown():
    x0, y0, w, h = 14, 0, 100, 210
    W, H = 1202, 1500
    s = max(w / W, h / H)
    ox = min(0, max(w - W * s, w / 2 - 0.53 * W * s))
    oy = min(0, max(h - H * s, h / 2 - 0.5 * H * s))
    pts = [('HAIR', '짧고 단정하게', 610, 540, 52), ('COAT', '검정 오버핏 롱코트', 640, 930, 100),
           ('TROUSERS', '네이비 와이드 팬츠', 640, 1370, 160), ('SHOES', '회색 스니커즈', 600, 1455, 186)]
    svg = ''
    for en, ko, px, py, ly in pts:
        cx, cy = x0 + ox + px * s, y0 + oy + py * s
        svg += f"<circle cx='{cx:.2f}' cy='{cy:.2f}' r='.8' class='dot'/><polyline points='{cx:.2f},{cy:.2f} 118,{ly} 124,{ly}' class='lbl'/>"
        svg += f"<text x='125.5' y='{ly + .9}' class='lbt'><tspan class='lbb'>{en}</tspan>  {ko}</text>"
    return ''.join([
        photo('FA-04', x0, y0, w, h, focus=(0.53, 0.5)),
        div(0, 0, 297, 210, f"<svg class='ov' viewBox='0 0 297 210'>{svg}</svg>", ''),
        photo('FA-03', 190, 22, 95, 86, focus=(0.6, 0.5)),
        t(170, 116, 116, 14, 'Front, or back?', 'h1'),
        t(170, 134, 116, 30, '<p>매장 안의 손님은</p><p>마네킹의 등을 먼저 본다.</p>', 'pull2'),
        t(170, 158, 112, 8, 'Inside the store, people meet the mannequin’s back first.', 'enb'),
        t(170, 170, 112, 16, '<p>그래서 나는 등을 먼저 입힌다 — 니트의 결, 어깨에서 떨어지는 품.</p>', 'kb'),
    ])


SWAP = {b4.p_four: p_four, b4.p_items: p_items, pe.p_breakdown: p_breakdown}
PAGES = [(SWAP.get(p, p), g) for p, g in b7.PAGES]
b7.PAGES = b6.PAGES = PAGES

CSS = b7.CSS + ".lt1{color:#EFE7DA}"


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for i, (p, g) in enumerate(PAGES):
        html, g = b7.page(i, p, g)
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    h = os.path.join(TMP, 'plan_b8.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B8</title><style>{CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b8.pdf'), os.path.join(TMP, 'plan_b8')], check=True)


if __name__ == '__main__':
    main()
