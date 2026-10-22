"""JAJU 포트폴리오 — 사진 벽 세 안: 같은 32장 + 글 한 칸을 서로 다른 조합 원리로 묶는다.

  python3 tools/jaju_layout/photo_wall_options.py   ->  docs/jaju_rounding_vmd/layout/photo_wall_options.pdf (3쪽)

사용자: "배치의 조합의 다양성을 두어 3가지 안을 제시하라."
  안 A  색과 시간 — 가로 세 줄: 밤 · 흑백 / 낮 · 흰 모형 / 노을 · 따뜻한 실내. 줄마다 빛이 하나.
  안 B  기둥과 띠 — 세로 기둥 여섯(사람 · 사람 · 사람 · 건축 · 건축 · 밤) 위에, 아래 띠 하나에 풍경 여덟. 무엇을 찍었나로 묶음.
  안 C  큰 한 장과 둘레 — 가운데 카누(PH-03)를 가장 크게, 위 · 아래 띠와 양쪽 기둥이 둘러쌈. 크기 대비.
기존 안(photo_wall.pdf)은 세 줄에 덩어리를 섞은 것 — 사례를 그대로 따른 안.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import photo_wall as pw  # noqa: E402

H, V, TEXT = pw.H, pw.V, pw.TEXT

A = V(
    (66, H((30, TEXT), (30, 'FA-01'), (44, V((1, 'PH-14'), (1, 'PH-13'))),
           (60, V((1, H((1, 'PH-08'), (1, 'PH-07'))), (1, H((1, 'PH-12'), (1, 'PH-02'))))),
           (50, V((1, 'AR-04'), (1, 'AR-05'))), (34, 'AR-01'))),
    (68, H((44, V((1, 'PH-16'), (1, 'PH-15'))), (50, 'AR-03'),
           (56, V((1, H((1, 'AR-10'), (1, 'AR-02'))), (1, H((1, 'AR-06'), (1, 'PH-17'))))),
           (46, V((1, 'AR-09'), (1, 'PH-05'))), (32, 'FA-03'), (32, 'FA-05'))),
    (70, H((56, 'PH-06'), (28, 'FA-04'), (36, V((1, 'PH-04'), (1, 'PH-09'), (1, 'PH-11'))),
           (40, V((1, 'AR-07'), (1, 'AR-08'))), (64, 'PH-03'), (42, V((1, 'PH-01'), (1, 'PH-10'))), (28, 'FA-02'))),
)

B = V(
    (150, H((46, V((54, TEXT), (80, 'FA-01'), (28, 'PH-02'))),
            (52, V((32, 'PH-06'), (74, 'FA-04'), (30, 'PH-11'), (28, 'PH-04'))),
            (50, V((70, 'FA-05'), (30, 'PH-17'), (66, 'FA-03'))),
            (54, V((40, 'AR-03'), (50, 'AR-10'), (38, 'AR-07'), (38, 'AR-06'))),
            (44, V((44, 'AR-02'), (44, 'AR-01'), (30, 'AR-08'), (52, 'FA-02'))),
            (46, V((1, 'AR-04'), (1, 'AR-05'), (1, 'AR-09'), (1, 'PH-14'), (1, 'PH-13'), (1, 'PH-08'), (1, 'PH-12'))))),
    (54, H((1, 'PH-16'), (1, 'PH-15'), (1, 'PH-09'), (1, 'PH-05'), (1, 'PH-01'), (1, 'PH-03'), (1, 'PH-10'), (1, 'PH-07'))),
)

C = H(
    (70, V((40, TEXT), (56, H((1, 'FA-01'), (1, 'FA-04'))), (22, H((1, 'PH-11'), (1, 'PH-04'))), (34, 'PH-06'),
           (52, H((1, 'FA-03'), (1, 'FA-02'))))),
    (150, V((26, H((1, 'PH-14'), (1, 'PH-13'), (1, 'PH-08'), (1, 'PH-12'), (1, 'PH-02'))), (112, 'PH-03'),
            (30, H((1, 'PH-16'), (1, 'PH-15'), (1, 'PH-09'), (1, 'PH-17'))), (30, H((1, 'PH-01'), (1, 'PH-05'), (1, 'PH-10'), (1, 'PH-07'))))),
    (72, V((60, H((1, 'FA-05'), (1, V((1, 'AR-10'), (1, 'AR-02'))))), (34, H((1, 'AR-03'), (1, 'AR-07'))),
           (30, H((1, 'AR-08'), (1, 'AR-06'), (1, 'AR-01'))), (60, V((1, 'AR-04'), (1, 'AR-05'), (1, 'AR-09'))))),
)

OPTIONS = [(A, '안 A · 색과 시간'), (B, '안 B · 기둥과 띠'), (C, '안 C · 큰 한 장과 둘레')]


def main():
    os.makedirs(pw.TMP, exist_ok=True)
    body = ''.join(f"<div class='sheet wall'>{pw.page(rows, tag)}</div>" for rows, tag in OPTIONS)
    h = os.path.join(pw.TMP, 'photo_wall_options.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU photo wall options</title><style>{pw.CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', pw.PRINT, h, os.path.join(pw.OUT, 'photo_wall_options.pdf'), os.path.join(pw.TMP, 'photo_wall_options')], check=True)


if __name__ == '__main__':
    main()
