"""JAJU 포트폴리오 — 사진 벽(단일 쪽): 사용자가 준 사례(사진가의 모자이크 포트폴리오 한 장)처럼, 지원자의 사진 32장을 한 면에.

  python3 tools/jaju_layout/photo_wall.py   ->  docs/jaju_rounding_vmd/layout/photo_wall.pdf

사례의 문법: 검정 바탕 · 가는 검정 틈 · 쪽 끝까지 꽉 찬 세 줄 · 줄마다 크기가 다른 덩어리(큰 한 장 / 2×2 / 세로 쌓기)를 섞음 ·
왼쪽 위 한 칸만 글 · 흑백과 컬러, 사람 · 풍경 · 밤을 섞되 비슷한 것끼리 한 덩어리로.
재료는 지원자의 것만(사진 PH-01–17 · 건축 AR-01–10 · 착장 FA-01–05). 표지 · 책 사진은 출처 확인 전이라 넣지 않는다.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_e as pe  # noqa: E402

pc, t, div, photo = pe.pc, pe.t, pe.div, pe.photo
OUT, TMP, PRINT, NAME = pe.OUT, pe.TMP, pe.PRINT, pe.NAME
M, G = 1.5, 1.2  # 바깥 테 · 틈 (mm)


def H(*kids):  # 가로로 나란히: (무게, 자식)
    return ('h', kids)


def V(*kids):  # 세로로 쌓기
    return ('v', kids)


TEXT = 'TEXT'
F = {'PH-02': (0.5, 0.6), 'PH-11': (0.6, 0.5), 'FA-01': (0.55, 0.55), 'FA-04': (0.53, 0.5), 'FA-05': (0.7, 0.6),
     'FA-02': (0.4, 0.4), 'FA-03': (0.6, 0.5), 'PH-17': (0.4, 0.6), 'AR-04': (0.5, 0.5), 'PH-06': (0.35, 0.5),
     'PH-03': (0.3, 0.55), 'PH-07': (0.33, 0.45), 'PH-05': (0.5, 0.55), 'PH-10': (0.46, 0.45)}

ROWS = V(
    (68, H((30, TEXT),
           (40, V((1, 'PH-11'), (1, 'PH-02'))),
           (30, 'FA-01'),
           (44, V((1, H((1, 'PH-04'), (1, 'PH-09'))), (1, H((1, 'PH-16'), (1, 'PH-15'))))),
           (30, 'FA-04'),
           (44, V((1, H((1, 'PH-14'), (1, 'PH-08'))), (1, H((1, 'PH-13'), (1, 'PH-12'))))),
           (46, V((1, 'AR-04'), (1, 'AR-05'), (1, 'AR-09'))))),
    (66, H((36, 'FA-05'),
           (52, V((1, H((1, 'AR-01'), (1, 'AR-10'))), (1, H((1, 'AR-02'), (1, 'AR-06'))))),
           (46, V((1, 'AR-03'), (1, 'AR-07'))),
           (34, 'FA-03'),
           (28, 'FA-02'),
           (60, V((1, 'AR-08'), (1, 'PH-17'))))),
    (70, H((74, 'PH-06'),
           (48, V((1, 'PH-07'), (1, 'PH-10'))),
           (84, 'PH-03'),
           (58, V((1, 'PH-01'), (1, 'PH-05'))))),
)


def place(node, x, y, w, h, out):
    if isinstance(node, str):
        out.append((node, x, y, w, h))
        return
    d, kids = node
    total = sum(k[0] for k in kids)
    room = (w if d == 'h' else h) - G * (len(kids) - 1)
    pos = x if d == 'h' else y
    for wt, child in kids:
        size = room * wt / total
        if d == 'h':
            place(child, pos, y, size, h, out)
        else:
            place(child, x, pos, w, size, out)
        pos += size + G


def text_tile(x, y, w, h):
    return div(x, y, w, h, ''.join([
        t(4, 4, w - 8, 4, 'FROM THE INSIDE', 'wm'),
        t(4, 14, w - 8, 30, '<p>가게 밖,</p><p>스쳐 지나가는</p><p>일상에서도 나는</p><p>사람들을</p><p>눈여겨본다.</p>', 'wk'),
        t(4, 38, w - 8, 14, 'Outside the shop, in everyday moments, I keep watching people.', 'we wrap'),
        t(4, h - 13, w - 8, 11, f'<p>PHOTO 17</p><p>ARCHITECTURE 10</p><p>STYLING 5</p><p>{NAME}</p>', 'wm'),
    ]), 'tile')


def page():
    cells = []
    place(ROWS, M, M, 297 - 2 * M, 210 - 2 * M, cells)
    o = []
    for pid, x, y, w, h in cells:
        o.append(text_tile(x, y, w, h) if pid == TEXT else photo(pid, round(x, 3), round(y, 3), round(w, 3), round(h, 3), focus=F.get(pid, (0.5, 0.5))))
    used = [c[0] for c in cells if c[0] != TEXT]
    assert len(used) == len(set(used)) == 32, (len(used), len(set(used)))
    return ''.join(o)


CSS = pe.CSS + """
.sheet.wall{background:#0B0B0B}.wall .ph{background:#1a1a1a}
.tile{background:#15120F;overflow:hidden}.tile div{position:absolute}
.wm{font-family:Mono,monospace;font-size:4.6pt;line-height:6.4pt;letter-spacing:.1em;color:#9A8F82;white-space:nowrap}.wm.r{text-align:right}
.wk{font-family:'WenQuanYi Zen Hei',sans-serif;font-weight:700;font-size:8.4pt;line-height:12.4pt;color:#EFE7DA}
.we{font-family:Lora,serif;font-style:italic;font-size:6pt;line-height:8.6pt;color:#9A8F82}.we p{white-space:normal}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'photo_wall.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU photo wall</title><style>{CSS}</style></head>"
                f"<body><div class='sheet wall'>{page()}</div></body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'photo_wall.pdf'), os.path.join(TMP, 'photo_wall')], check=True)


if __name__ == '__main__':
    main()
