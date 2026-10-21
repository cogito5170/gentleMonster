"""JAJU 포트폴리오 표지 — 검은 바탕 띠와 제목 · 메시지 세 줄을 뺀 판 (사용자 지시, 2026-10-21).

  python3 tools/jaju_layout/cover_clean.py   ->  docs/jaju_rounding_vmd/layout/cover_clean.pdf (표지 한 쪽)

B안 표지(tools/p1_layout/cover_options.py b_cover)에서 뺀 것:
  - 아래쪽 검은 바탕 (사진 띠 0–142 mm 아래)
  - "From the inside" · "밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다." · 영문 한 줄
남긴 것: 사진(이제 전면) · 위 구석 작은 표기 둘 · 오른쪽 아래 이름 · 직무.
사진 비율(1296×912 ≈ 1.42)이 A4 가로(1.414)와 거의 같아 전면에 잘림 없이 들어간다.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, os.path.join(REPO, 'tools/p1_layout'))

import cover_options as co  # noqa: E402

OUT = os.path.join(REPO, 'docs/jaju_rounding_vmd/layout')
TMP = os.path.join(REPO, 'out/jaju_layout')
t = co.t


def cover_clean():
    return ''.join([
        co.photo(0, 0, 297, 210, crop=(0.5, 0.5)),
        "<div class='shade'></div>",
        t(8, 5.5, 80, 4, 'FROM THE INSIDE', 'tiny w'), t(209, 5.5, 80, 4, '2026', 'tiny w r'),
        t(207, 193, 80, 5, '<b>JEONG HYEOKJU</b>', 'gname r'),
        t(187, 198, 100, 5, 'Visual Merchandiser Portfolio', 'gen r cw'),
    ])


CSS = co.CSS + """
.shade{left:0;top:0;width:297mm;height:210mm;background:linear-gradient(to top,rgba(0,0,0,.45),rgba(0,0,0,0) 22%)}
.cw{color:#e6e6e6}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'cover_clean.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><style>{CSS}</style></head>"
                f"<body><div class='sheet'>{cover_clean()}</div></body></html>")
    subprocess.run(['node', os.path.join(REPO, 'tools/p1_layout/print_pdf.mjs'), h,
                    os.path.join(OUT, 'cover_clean.pdf'), os.path.join(TMP, 'cover_clean')], check=True)


if __name__ == '__main__':
    main()
