"""JAJU 포트폴리오 — B8: B7 그대로, 02 Observe 의 한 문장만 바꾼 판.

  python3 tools/jaju_layout/plan_b8.py   ->  docs/jaju_rounding_vmd/layout/plan_b8.pdf

사용자: "기존으로 복구한다. 01 observe 의 concept 은 '일상에서 사람들을 관찰하는 시선을 가졌다.'의 맥락으로 간다.
자기소개서, 포트폴리오를 참고하여 적절한 문장으로 임의 판단하에 수정한다."
  전  틈 너머로, 사람들이 멈춘 자리를 본다.            / Through the gap, I watch where people stop.
  후  가게 밖, 스쳐 지나가는 일상에서도 나는 사람들을 눈여겨본다.  / Outside the shop, in everyday moments, I keep watching people.
근거: '스쳐 지나가던 일상' — docs/portfolio/philosophy.md 28행, '눈여겨보다' — 자기소개서 1번(jaju_rounding_vmd_Q1-3_draft.md),
'나는 안에서 본다' — 01 Prologue. 문장 말고는 B7 과 같다.
"""
import os
import subprocess

import plan_b7 as b7

pe, t, OUT, TMP, PRINT = b7.pe, b7.t, b7.OUT, b7.TMP, b7.PRINT

OBSERVE = [('틈 너머로, 사람들이 멈춘 자리를 본다.', '가게 밖, 스쳐 지나가는 일상에서도 나는 사람들을 눈여겨본다.'),
           ('Through the gap, I watch where people stop.', 'Outside the shop, in everyday moments, I keep watching people.')]


def page(i, p, g):
    html, g = b7.page(i, p, g)
    if i == 2:
        for a, b in OBSERVE:
            assert a in html, a
            html = html.replace(a, b)
    return html, g


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for i, (p, g) in enumerate(b7.PAGES):
        html, g = page(i, p, g)
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    h = os.path.join(TMP, 'plan_b8.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B8</title><style>{b7.CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b8.pdf'), os.path.join(TMP, 'plan_b8')], check=True)


if __name__ == '__main__':
    main()
