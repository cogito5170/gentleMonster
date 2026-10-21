"""JAJU 포트폴리오 — B11: 기존 안(B10) 그대로, (1) 03 Where people stop 의 빈 칸 셋을 사진으로 채워 9장, (2) 바탕을 자주 스타일 안 2 의
미색으로 바꾸고 글자색만 바꾼 판.

  python3 tools/jaju_layout/plan_b11.py   ->  docs/jaju_rounding_vmd/layout/plan_b11.pdf

사용자: "1. '기존 안' 4페이지의 누락된 이미지를 복구하여 총 9개의 이미지를 완성하라.
        2. '기존 안'의 배경 색을 '자주 스타일 안 2'로 맞추고, 텍스트의 색상만 변경하라."
  (1) B10 에서 비운 칸(1행 3열 · 2행 1열 · 3행 2열)에 B9 까지 있던 PH-09 · PH-16 · PH-12 를 되돌림. 번호는 읽는 순서(행 → 열)로.
      B9 의 나머지 하나 PH-15(놀이터)는 사람이 없어 남겨 둠.
  (2) 바탕 #15120F → #F6F2EC(자주 스타일 안 2). 바탕 위 글자: 크림 → #2B2622, 회갈색 → #7A716A. 주황 강조는 그대로.
      사진 위 글자(파트 표지 · 표지 머리 · 사진 위 바닥 줄 · 사진 속 표시)는 사진 위에 있으므로 그대로 크림.
      08 A room 의 글 상자는 글자의 바탕이라 미색 반투명으로.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b10 as b10  # noqa: E402

pe = b10.pe
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT

# ── (1) 03 의 아홉 칸 ────────────────────────────────────────────────────────────────
b10.PEOPLE = sorted(b10.PEOPLE + [
    ('PH-09', (0, 2), (0.5, 0.55), 'Kiddie train', '비 갠 뒤, 물웅덩이 옆에 작은 기차가 서 있다.'),
    ('PH-16', (1, 0), (0.5, 0.5), 'Seawall', '색칠한 방파제 벽을 따라 길이 이어진다.'),
    ('PH-12', (2, 1), (0.5, 0.5), 'Overpass', '육교 아래로 오토바이 한 대가 지나간다.'),
], key=lambda c: c[1])

# ── (2) 바탕 · 글자색 ────────────────────────────────────────────────────────────────
PAPER, INK, SUB, FAINT = '#F6F2EC', '#2B2622', '#7A716A', '#A69C92'
TOP_MAST = re.compile(r"class='t mast( r)?' (style='left:(?:14|163)mm;top:8mm;)")  # 표지 · 뒤표지 맨 위, 사진 위


def page(i, p, g):
    html, g = b10.page(i, p, g)
    return TOP_MAST.sub(lambda m: f"class='t mast lt{m.group(1) or ''}' {m.group(2)}", html), g


CSS = b10.CSS + f"""
/* 바탕 — 자주 스타일 안 2 */
.sheet,.bg{{background:{PAPER}}}
/* 바탕 위 글자 */
body,.mast,.cvt,.cvt2,.cvk,.letter,.pt.dk,.pullbig,.abt .ab span,.imname,.clist .ct2,.h3,.contact .nm,.tri .tw,.giant,.lt1x,
.cc .ct,.cell,.data .hx,.cap b{{color:{INK}}}
.cve,.enb,.ft,.data,.pn2,.side,.keys .k span,.cc,.pal span,.cell.void,.note,.mast.dim,.note2,.abt .ab b,.clist .ck,.clist .cp,
.contact,.tri .tk,.credit,.cap{{color:{SUB}}}
.cap .n{{color:{FAINT}}}
.kb,.prose{{-webkit-text-stroke:.15pt {INK}}}
.ghost{{-webkit-text-stroke:.35pt rgba(43,38,34,.2)}}
.ov .lbt{{fill:{INK}}}.ov .hlt{{fill:{SUB}}}
/* 사진 위 글자는 그대로 */
.mast.lt,.ft.lt,.data.lt,.pt,.lt1{{color:#F6F0E6}}.pt.dk{{color:#1E1914}}
/* 08 의 글 상자 — 글자의 바탕 */
.frost{{background:rgba(246,242,236,.88);border:.15mm solid rgba(43,38,34,.12)}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for i, (p, g) in enumerate(b10.PAGES):
        html, g = page(i, p, g)
        if i == 3:
            html = html.replace('17 FRAMES · 06 SHOWN', '17 FRAMES · 09 SHOWN')
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    h = os.path.join(TMP, 'plan_b11.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B11</title><style>{CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b11.pdf'), os.path.join(TMP, 'plan_b11')], check=True)


if __name__ == '__main__':
    main()
