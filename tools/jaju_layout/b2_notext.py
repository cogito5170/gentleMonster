"""기존 안(B2)에서 글자를 모두 뺀 판 — 사진 · 표시 선 · 도형만 남긴다 (사용자 지시, 2026-10-21).

  python3 tools/jaju_layout/b2_notext.py   ->  docs/jaju_rounding_vmd/layout/plan_b2_notext.pdf

book_b2.py 로 B2 를 다시 짓고, 그때 나온 HTML 마다 '글자 숨김' CSS 를 덧붙여 다시 인쇄한다.
숨기는 것: 모든 글 상자(.t) · SVG 안의 글자(<text>) · 팔레트 이름. 남기는 것: 사진 · 초점 원 · 점선 틀 · 선 · 도형 · 색칩.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import book_b2 as b2  # noqa: E402

TMP, OUT = b2.TMP, b2.OUT
PARTS = ['b2_cover', 'ch1_photo', 'b2_contain_open', 'b2_contain', 'b2_fill_open', 'b2_rest']
HIDE = '<style>.t,.pal span,svg text{display:none!important}</style></head>'


def main():
    b2.main()
    pdfs = []
    for name in PARTS:
        src = os.path.join(TMP, name + '.html')
        with open(src, encoding='utf-8') as f:
            html = f.read()
        dst = os.path.join(TMP, name + '_notext.html')
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(html.replace('</head>', HIDE, 1))
        pdf = os.path.join(TMP, name + '_notext.pdf')
        subprocess.run(['node', b2.c1.PRINT, dst, pdf, os.path.join(TMP, name + '_notext')], check=True)
        pdfs.append(pdf)
    out = os.path.join(OUT, 'plan_b2_notext.pdf')
    subprocess.run(['pdfunite', *pdfs, out], check=True)
    print('wrote', out)


if __name__ == '__main__':
    main()
