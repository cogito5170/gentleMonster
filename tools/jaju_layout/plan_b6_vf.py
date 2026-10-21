"""JAJU 포트폴리오 — B6 + 뷰파인더: B6 를 그대로 두고, 파트 대표 쪽(02 Observe · 06 Contain · 09 Fill)에만 네 모서리 표시.

  python3 tools/jaju_layout/plan_b6_vf.py   ->  docs/jaju_rounding_vmd/layout/plan_b6_vf.pdf

사용자: "기존 B6 로 복구한다. 단, 각 파트의 대표 페이지에만 B6 의 상하 선과 이어지도록 뷰파인더 효과를 넣어라."
B7 의 격자 · 보정 · 출처 띠 · Often · 크레디트는 모두 빼고, 모서리 표시만 B7 에서 위 · 아래 선이 있던 자리(y 12 · 195,
x 14 · 283)에 둔다 — 바닥 줄(y 199) 바로 위에서 닫힌다.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b6 as b6  # noqa: E402

b5, pe = b6.b5, b6.pe
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT
PARTS = {2, 6, 9}  # /01 Observe · /02 Contain · /03 Fill


def corner(x, y, dx, dy, r=6):
    pts = f'{x + dx * r},{y} {x},{y} {x},{y + dy * r}'
    return f"<polyline points='{pts}' class='vfs'/><polyline points='{pts}' class='vf'/>"  # 밝은 사진 위에서도 보이게 어두운 밑선


def viewfinder():
    g = corner(14, 12, 1, 1) + corner(283, 12, -1, 1) + corner(14, 195, 1, -1) + corner(283, 195, -1, -1)
    return pe.div(0, 0, 297, 210, f"<svg class='ov' viewBox='0 0 297 210'>{g}</svg>", '')


CSS = b5.CSS + ".ov .vf{fill:none;stroke:rgba(239,231,218,.9);stroke-width:.3}.ov .vfs{fill:none;stroke:rgba(21,18,15,.35);stroke-width:.9}"


def main():
    os.makedirs(TMP, exist_ok=True)
    body = ''.join(f"<div class='sheet {g}'>{b6.page(i, p, g)}{viewfinder() if i in PARTS else ''}</div>"
                   for i, (p, g) in enumerate(b6.PAGES))
    h = os.path.join(TMP, 'plan_b6_vf.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B6 viewfinder</title><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b6_vf.pdf'), os.path.join(TMP, 'plan_b6_vf')], check=True)


if __name__ == '__main__':
    main()
