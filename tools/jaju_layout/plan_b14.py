"""JAJU 포트폴리오 — B14: B13 그대로, 맨 앞 표지의 사진만 사용자가 준 흑백 사진으로 바꾼 판.

  python3 tools/jaju_layout/plan_b14.py   ->  docs/jaju_rounding_vmd/layout/plan_b14.pdf

사용자: "맨 처음 커버 페이지를 해당 이미지로 대체한다. 이미지 다른 것은 추가하지 않는다."
새 사진: docs/jaju_rounding_vmd/assets/cover/cover_bw.jpg (1296×912, 기존 표지 사진과 같은 장면 · 같은 크기의 흑백판).
바꾸는 곳은 표지 한 쪽뿐 — 14 Often 의 N°01 과 뒤표지(좌우 뒤집음)는 기존 컬러 표지 사진 그대로.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b13 as b13  # noqa: E402

b10 = b13.b10
b3, pe = b10.b8.b3, b10.pe
pc = pe.pc
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT
COVER_BW = os.path.join(pc.REPO if hasattr(pc, 'REPO') else os.path.abspath(os.path.join(HERE, '../..')),
                        'docs/jaju_rounding_vmd/assets/cover/cover_bw.jpg')

_path = pc.path


def path(pid):
    return COVER_BW if pid == 'COVER-BW' else _path(pid)


pc.path = path


def p_cover():
    return b3.p_cover().replace(pc.screen('COVER'), pc.screen('COVER-BW'), 1)


PAGES = [(p_cover, '')] + b13.PAGES[1:]


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for i, (p, g) in enumerate(PAGES):
        html, g = b10.page(i, p, g)
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    h = os.path.join(TMP, 'plan_b14.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B14</title><style>{b13.CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b14.pdf'), os.path.join(TMP, 'plan_b14')], check=True)


if __name__ == '__main__':
    main()
