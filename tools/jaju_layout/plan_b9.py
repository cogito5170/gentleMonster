"""JAJU 포트폴리오 — B9: B8 그대로, 02 Observe 여는 면의 문장만 2-2 세션(스토리)에서 정한 문장으로.

  python3 tools/jaju_layout/plan_b9.py   ->  docs/jaju_rounding_vmd/layout/plan_b9.pdf

사용자(2-2 세션): "01 observe 의 concept 은 '일상에서 사람들을 관찰하는 시선을 가졌다.'의 맥락으로 간다."
사용자(이 세션): "2-2 세션으로 받은 스토리 라인을 고려하여 수정하는 작업을 진행하라."
  전  틈 너머로, 사람들이 멈춘 자리를 본다. / Through the gap, I watch where people stop.
  후  가게 밖, 스쳐 지나가는 일상에서도 나는 사람들을 눈여겨본다. / Outside the shop, in everyday moments, I keep watching people.
다른 쪽 · 장 1 의 구성(03 · 04 · 05)은 그대로. 이유: docs/jaju_rounding_vmd/plan_b9.md
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b8 as b8  # noqa: E402

b7, b5, pe = b8.b7, b8.b5, b8.pe
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT

OLD = ('틈 너머로, 사람들이 멈춘 자리를 본다.', 'Through the gap, I watch where people stop.')
NEW = ('가게 밖, 스쳐 지나가는 일상에서도 나는 사람들을 눈여겨본다.', 'Outside the shop, in everyday moments, I keep watching people.')


def p_observe():
    html = b5.p_observe()
    for a, b in zip(OLD, NEW):
        assert a in html, a
        html = html.replace(a, b, 1)
    return html


PAGES = [(p_observe if p is b5.p_observe else p, g) for p, g in b8.PAGES]
b8.PAGES = b7.PAGES = b7.b6.PAGES = PAGES


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for i, (p, g) in enumerate(PAGES):
        html, g = b7.page(i, p, g)
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    h = os.path.join(TMP, 'plan_b9.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B9</title><style>{b8.CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b9.pdf'), os.path.join(TMP, 'plan_b9')], check=True)


if __name__ == '__main__':
    main()
