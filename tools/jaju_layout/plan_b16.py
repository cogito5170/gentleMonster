"""JAJU 포트폴리오 — B16: B15 그대로, 표지 다음에 사진 한 장만 있는 쪽을 새로 넣은 판 (18쪽).

  python3 tools/jaju_layout/plan_b16.py   ->  docs/jaju_rounding_vmd/layout/plan_b16.pdf

사용자: "2페이지를 새로 추가한 후 해당 이미지를 첨부하라. 이미지만 존재한다."
새 사진: docs/jaju_rounding_vmd/assets/cover/opening_book.jpg (1456×816, 표지 사진이 실린 책을 펼쳐 든 장면).
- 쪽 전체에 사진 한 장, 글 · 바탕 · 쪽 번호 없음(표지와 같은 규칙). 쪽 비율(1.41)보다 사진이 넓어(1.78) 좌우가 잘린다.
- 본문 쪽 번호는 그대로(Prologue = 01): 사진만 있는 두 쪽은 번호를 세지 않는다. 그래서 프롤로그의 p.02 · p.06 · p.09 도 그대로 맞다.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b15 as b15  # noqa: E402

b14, b13, b10 = b15.b14, b15.b13, b15.b10
pe, pc = b10.pe, b10.pe.pc
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT
OPENING = os.path.abspath(os.path.join(HERE, '../../docs/jaju_rounding_vmd/assets/cover/opening_book.jpg'))

_path = pc.path


def path(pid):
    return OPENING if pid == 'OPENING' else _path(pid)


pc.path = path


def p_opening():
    return pe.photo('OPENING', 0, 0, 297, 210, focus=(0.47, 0.5))


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for i, (p, g) in enumerate(b15.PAGES):  # 기존 17쪽은 원래 번호(i)로 만든다
        html, g = b10.page(i, p, g)
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    sheets.insert(1, f"<div class='sheet'>{p_opening()}</div>")
    h = os.path.join(TMP, 'plan_b16.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B16</title><style>{b13.CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b16.pdf'), os.path.join(TMP, 'plan_b16')], check=True)


if __name__ == '__main__':
    main()
