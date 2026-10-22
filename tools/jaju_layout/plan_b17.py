"""JAJU 포트폴리오 — B17: B16 그대로, 쪽 번호를 표지부터 센 번호로 바꾼 판 (18쪽).

  python3 tools/jaju_layout/plan_b17.py   ->  docs/jaju_rounding_vmd/layout/plan_b17.pdf

사용자: "커버를 포함해서 페이지 수를 카운트한다."
  표지 = 1, 책 사진 = 2, Prologue = 3 … 뒤표지 = 18. 바닥 줄 번호 01–15 → 03–17.
  안의 쪽 참조도 같이: 프롤로그 p.02 · p.06 · p.09 → p.04 · p.08 · p.11, Proposal 의 ← 05 · 08 · 12 → 07 · 10 · 14.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b16 as b16  # noqa: E402

b15, b13, b10 = b16.b15, b16.b13, b16.b10
OUT, TMP, PRINT = b10.pe.OUT, b10.pe.TMP, b10.pe.PRINT
SHIFT = 2
FOOT = re.compile(r"(class='t ft(?: lt)? r'[^>]*>)(\d\d)(</div>)")
REF = re.compile(r"(p\.|← )(\d\d)")


def renumber(html):
    html = FOOT.sub(lambda m: f'{m.group(1)}{int(m.group(2)) + SHIFT:02d}{m.group(3)}', html)
    return REF.sub(lambda m: f'{m.group(1)}{int(m.group(2)) + SHIFT:02d}', html)


def sheets():
    out = []
    for i, (p, g) in enumerate(b15.PAGES):
        html, g = b10.page(i, p, g)
        out.append(f"<div class='sheet {g}'>{renumber(html)}</div>")
    out.insert(1, f"<div class='sheet'>{b16.p_opening()}</div>")
    return out


def main():
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'plan_b17.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B17</title><style>{b13.CSS}</style></head><body>{''.join(sheets())}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b17.pdf'), os.path.join(TMP, 'plan_b17')], check=True)


if __name__ == '__main__':
    main()
