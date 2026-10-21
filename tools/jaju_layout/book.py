"""JAJU 포트폴리오 — 지금까지의 쪽을 한 PDF 로 잇는다.

  python3 tools/jaju_layout/book.py   ->  docs/jaju_rounding_vmd/layout/jaju_portfolio_draft.pdf

  표지 · 1쪽   B안 (tools/p1_layout/cover_options.py 의 b_cover · b_page1 — InDesign 판 cover_b 와 같은 값)
  2–4쪽       장 1 · 사진 — 관찰하다 (ch1_photo.py)
  5–7쪽       장 2 · 건축 — 담다 (ch2_arch.py)
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, os.path.join(REPO, 'tools/p1_layout'))

import ch1_photo  # noqa: E402
import ch2_arch  # noqa: E402
import cover_options as co  # noqa: E402

OUT = ch1_photo.OUT
TMP = ch1_photo.TMP


def cover_pdf():
    body = ''.join(f"<div class='sheet'>{p}</div>" for p in (co.b_cover(), co.b_page1()))
    h = os.path.join(TMP, 'book_cover.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><style>{co.CSS}</style></head><body>{body}</body></html>")
    pdf = os.path.join(TMP, 'book_cover.pdf')
    subprocess.run(['node', ch1_photo.PRINT, h, pdf], check=True)
    return pdf


def main():
    os.makedirs(TMP, exist_ok=True)
    parts = [cover_pdf()]
    ch1_photo.main()
    parts.append(os.path.join(OUT, 'ch1_photo.pdf'))
    ch2_arch.main()
    parts.append(os.path.join(OUT, 'ch2_arch.pdf'))
    out = os.path.join(OUT, 'jaju_portfolio_draft.pdf')
    subprocess.run(['pdfunite', *parts, out], check=True)
    print('wrote', out)


if __name__ == '__main__':
    main()
