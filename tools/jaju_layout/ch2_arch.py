"""JAJU 포트폴리오 장 2 · 건축 — 담다 (5–7쪽) 시안 PDF.

  python3 tools/jaju_layout/ch2_arch.py   ->  docs/jaju_rounding_vmd/layout/ch2_arch.pdf

  5쪽  여는 면   장 1(2쪽)과 같은 틀 + 사례 3(NEA)의 개념 도해: 틀 → 비움 → 채움
  6쪽  콜라주    도시에서 방까지 — 크기가 다른 사진을 엇갈리게 (NEA 본문 면 · ETÉREO COLLAGE)
  7쪽  디테일    방 안의 진열을 VMD 의 눈으로: 눈높이 · 초점 · 빛 · 동선 (장 1 4쪽과 같은 표시 언어)

장 1 의 도구(ch1_photo.py: 지면 · 사진 틀 · 표시)를 그대로 쓴다. 사진만 assets/arch 에서 읽는다.
"""
import os
import subprocess

import ch1_photo as c

ARCH = os.path.join(c.REPO, 'docs/jaju_rounding_vmd/assets/arch')
t, photo, corners, focal, dash, head, e = c.t, c.photo, c.corners, c.focal, c.dash, c.head, c.e
LABEL = '02 — CONTAIN'


def diagram(x, y, w, h):
    """개념 도해 (사례 3 NEA 의 사이 면을 축소): 틀 → 비움 → 채움. 가는 선 + 단어, 가운데 빈 칸은 점선."""
    cx = [w * 0.12, w * 0.5, w * 0.88]
    cy = h * 0.42
    sq = 9
    words = [('Frame', '틀'), ('Void', '비움'), ('Fill', '채움')]
    o = ''
    for i, (en, ko) in enumerate(words):
        cls = 'ds' if i == 1 else 'dl'
        fill = "<rect x='{:.2f}' y='{:.2f}' width='{:.2f}' height='{:.2f}' class='df'/>".format(cx[i] - sq / 2 + 1.6, cy - sq / 2 + 1.6, sq - 3.2, sq - 3.2) if i == 2 else ''
        o += f"<rect x='{cx[i] - sq / 2:.2f}' y='{cy - sq / 2:.2f}' width='{sq}' height='{sq}' class='{cls}'/>{fill}"
        o += f"<text x='{cx[i]:.2f}' y='{cy + sq / 2 + 5:.2f}' text-anchor='middle' class='dw'>{en}</text>"
        o += f"<text x='{cx[i]:.2f}' y='{cy + sq / 2 + 8.6:.2f}' text-anchor='middle' class='dk'>{ko}</text>"
    for a, b in ((0, 1), (1, 2)):
        x1, x2 = cx[a] + sq / 2 + 2, cx[b] - sq / 2 - 2
        o += f"<line x1='{x1:.2f}' y1='{cy:.2f}' x2='{x2:.2f}' y2='{cy:.2f}' class='dl'/>"
        o += f"<path d='M{x2 - 1.6:.2f},{cy - 1:.2f} L{x2:.2f},{cy:.2f} L{x2 - 1.6:.2f},{cy + 1:.2f}' class='dl'/>"
    return c.div(x, y, w, h, f"<svg class='dg' viewBox='0 0 {w} {h}'>{o}</svg>")


# ── 5쪽 · 여는 면 ───────────────────────────────────────────────────────────────────
def page5():
    def m(to, s):  # AR-03: 격자 골조 — 나무 판으로 채운 칸과 비운 칸
        fx, fy = to(1040, 600)
        vx, vy = to(870, 380)
        return (corners(178, 148) + dash(*to(1020, 560), 330 * s, 230 * s)
                + f"<text x='{fx - 1:.1f}' y='{fy - 4.2:.1f}' class='lb'>Fill</text>"
                + dash(*to(790, 300), 190 * s, 150 * s) + f"<text x='{vx - 1:.1f}' y='{vy - 3:.1f}' class='lb'>Void</text>")

    return ''.join([
        head(5, LABEL),
        t(18, 54, 80, 30, '02', 'chno'),
        t(18, 92, 90, 12, 'Contain', 'chtitle'),
        t(18, 105, 90, 8, '담다', 'chko'),
        t(18, 124, 84, 30, '<p>멈춘 자리에는 늘 틀이 있었다.</p><p>무엇을 채우고 무엇을 비울지가 그 안의 하루를 정한다.</p>', 'body'),
        t(18, 141, 84, 20, '<p>Where people stop, there is always a frame.</p><p>What fills it, and what is left empty, shapes the day inside.</p>', 'bodyen'),
        diagram(18, 158, 80, 30),
        photo('AR-03', 109, 31, 178, 148, focus=(0.55, 0.5), marks=m),
        t(109, 182, 178, 5, '<b>AR-03</b>&nbsp;&nbsp;격자 골조와 나무 판 · 모형', 'cap'),
    ])


# ── 6쪽 · 도시에서 방까지 ─────────────────────────────────────────────────────────────
def page6():
    def yard(to, s):  # AR-06: 두 건물 사이를 비운 마당
        x0, y0 = to(380, 140)
        return dash(x0, y0, 330 * s, 400 * s) + f"<text x='{x0 + 1.5:.1f}' y='{y0 + 4:.1f}' class='lb'>Courtyard</text>"

    def red(to, s):  # AR-09: 회색 광장의 빨간 조각
        cx, cy = to(1525, 715)
        return focal(cx, cy, 4.4)

    items = [  # 넓은 데서 좁은 데로: 도시 → 마당 → 길 → 집
        ('AR-09', 100, 31, 120, 54, (0.5, 0.5), red, '01', 'City', '도시의 광장'),
        ('AR-06', 226, 31, 61, 54, (0.5, 0.45), yard, '02', 'Courtyard', '건물 사이의 마당'),
        ('AR-05', 100, 99, 87, 43, (0.45, 0.5), '', '03', 'Path', '매스를 잇는 회랑과 길'),
        ('AR-10', 193, 99, 43, 43, (0.5, 0.5), '', '04', 'House', '골목 언덕의 집'),
        ('AR-02', 242, 99, 45, 43, (0.6, 0.5), '', '05', 'Hollow', '도시 아래를 비운 단면'),
    ]
    cells = []
    for pid, x, y, w, h, f, mk, n, word, ko in items:
        cells.append(photo(pid, x, y, w, h, focus=f, marks=mk))
        cells.append(t(x, y + h + 1.8, w, 4, f"<b>{n}</b>&nbsp;&nbsp;{word}<span class='pid'>{pid}</span>", 'gcap'))
    return ''.join([
        head(6, LABEL),
        t(18, 31, 72, 6, 'From the city to the room', 'h'),
        t(18, 40, 76, 40, '<p>도시에서 마당으로, 마당에서 길과 집으로.</p><p>틀을 좁혀 갈수록</p><p>그 안에 사는 사람의 하루가 보인다.</p>', 'body'),
        t(18, 62, 74, 20, '<p>From the city to the yard, to the path and the house.</p><p>The narrower the frame, the clearer the day inside.</p>', 'bodyen'),
        t(18, 150, 74, 30, '<p><b>City · Courtyard · Hollow</b>&nbsp; 비워 둔 자리</p><p><b>Path · House</b>&nbsp; 사람이 지나고 머무는 자리</p>', 'key'),
        *cells,
        t(100, 160, 187, 20, '<p>모형 · 렌더 — 건축학과 작업. 프로젝트 이름 · 학년 ____</p>', 'note'),
    ])


# ── 7쪽 · 방 안의 진열 ───────────────────────────────────────────────────────────────
def page7():
    def living(to, s):  # AR-07: 거실 · 식당
        ey = to(0, 455)[1]
        lx, ly = to(548, 405)
        tx, ty = to(550, 505)
        return (corners(178, 100)
                + f"<line x1='3' y1='{ey:.1f}' x2='175' y2='{ey:.1f}' class='gl'/><text x='4' y='{ey - 1.4:.1f}' class='lb'>a)  Eye level</text>"
                + focal(lx, ly, 3.6) + f"<text x='{lx + 5:.1f}' y='{ly + 1:.1f}' class='lb'>d)  Light</text>"
                + dash(*to(470, 480), 165 * s, 70 * s) + f"<text x='{tx - 13:.1f}' y='{ty + 12.5:.1f}' class='lb'>c)  Set</text>")

    def kitchen(to, s):  # AR-08: 주방 — 빨간 후드
        cx, cy = to(627, 222)
        return focal(cx, cy, 5.4) + f"<text x='{cx + 7:.1f}' y='{cy + 1:.1f}' class='lb'>b)</text>"

    return ''.join([
        head(7, LABEL),
        t(18, 31, 72, 6, 'A room, set like a display', 'h'),
        t(18, 40, 76, 40, '<p>방 안에도 진열이 있다.</p><p>눈높이에 무엇을 두고, 어디에 빛을 주고,</p><p>어떤 물건을 한 자리에 모을지.</p>', 'body'),
        t(18, 62, 74, 20, '<p>A room is a display too: what sits at eye level,</p><p>where the light falls, what is set together.</p>', 'bodyen'),
        t(18, 92, 74, 46,
          "<div class='k'><b>a)</b> Eye level<span>눈이 머무는 높이</span></div>"
          "<div class='k'><b>b)</b> Red point<span>빨간 후드 — 시선이 먼저 닿는 곳</span></div>"
          "<div class='k'><b>c)</b> Set<span>식탁 · 의자 · 책 — 한 자리에 모은 조합</span></div>"
          "<div class='k'><b>d)</b> Light<span>스탠드 하나의 빛</span></div>", 'keys'),
        t(18, 160, 86, 20, '<p>틀을 지었으니 이제 채운다. 다음 장에서 나는 그 자리를 옷으로 채운다.</p>', 'bridge'),
        photo('AR-07', 109, 31, 178, 100, focus=(0.5, 0.55), marks=living),
        photo('AR-08', 109, 136, 87.5, 44, focus=(0.55, 0.38), marks=kitchen),
        photo('AR-01', 199.5, 136, 87.5, 44, focus=(0.55, 0.45)),
        t(109, 181, 87.5, 4, 'b)  Red point — 주방 모형 (AR-08)', 'gcap'),
        t(199.5, 181, 87.5, 4, 'Layer — 겹쳐 쌓은 판과 빛 (AR-01)', 'gcap'),
    ])


EXTRA_CSS = """
.dg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.dg .dl{fill:none;stroke:#8a8a8a;stroke-width:.3}.dg .ds{fill:none;stroke:#fff;stroke-width:.35;stroke-dasharray:1.2 .9}
.dg .df{fill:#CFCFCF}.dg .dw{font-family:Inst,sans-serif;font-size:2.9px;fill:#fff}
.dg .dk{font-family:Inst,'WenQuanYi Zen Hei',sans-serif;font-size:2.3px;fill:#8a8a8a}
.note{font-size:6pt;color:#555}
"""


def main():
    c.PHOTO = ARCH
    os.makedirs(c.TMP, exist_ok=True)
    body = ''.join(f"<div class='sheet'>{p()}</div>" for p in (page5, page6, page7))
    h = os.path.join(c.TMP, 'ch2_arch.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU ch2 arch</title><style>{c.CSS}{EXTRA_CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', c.PRINT, h, os.path.join(c.OUT, 'ch2_arch.pdf'), os.path.join(c.TMP, 'ch2_arch')], check=True)


if __name__ == '__main__':
    main()
