"""JAJU 포트폴리오 — B12: B10(기존 안, 어두운 바탕) 그대로, 03 Where people stop 의 빈 칸 셋만 사진으로 채워 9장.

  python3 tools/jaju_layout/plan_b12.py   ->  docs/jaju_rounding_vmd/layout/plan_b12.pdf

사용자: "B10 으로 복구한다. 9개의 그리드에 빠진 이미지를 보충하라."
B11 의 (1)만 쓰고 (2) 미색 바탕 · 글자색은 쓰지 않는다. 채운 사진 · 캡션은 B11 과 같다(plan_b11.md).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b10 as b10  # noqa: E402

pe = b10.pe
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT

b10.PEOPLE = sorted(b10.PEOPLE + [
    ('PH-09', (0, 2), (0.5, 0.55), 'Kiddie train', '비 갠 뒤, 물웅덩이 옆에 작은 기차가 서 있다.'),
    ('PH-16', (1, 0), (0.5, 0.5), 'Seawall', '색칠한 방파제 벽을 따라 길이 이어진다.'),
    ('PH-12', (2, 1), (0.5, 0.5), 'Overpass', '육교 아래로 오토바이 한 대가 지나간다.'),
], key=lambda c: c[1])


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for i, (p, g) in enumerate(b10.PAGES):
        html, g = b10.page(i, p, g)
        if i == 3:
            html = html.replace('17 FRAMES · 06 SHOWN', '17 FRAMES · 09 SHOWN')
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    h = os.path.join(TMP, 'plan_b12.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B12</title><style>{b10.CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b12.pdf'), os.path.join(TMP, 'plan_b12')], check=True)


if __name__ == '__main__':
    main()
