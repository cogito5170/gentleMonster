"""JAJU 포트폴리오 장 1 · 사진 — 관찰하다 (2–4쪽) 시안 PDF.

  python3 tools/jaju_layout/ch1_photo.py   ->  docs/jaju_rounding_vmd/layout/ch1_photo.pdf

  2쪽  여는 면   가장 강한 한 장 + 장 번호 · 제목 · 한 문장 (Galatasaray 의 여는 사진 + 제목)
  3쪽  격자      같은 크기 9장 · 한 낱말씩 (Galatasaray 의 10–99 표 — 말 대신 수로)
  4쪽  디테일    점선 틀 · 초점 원으로 '무엇에 멈췄나' (JAJU 의 뷰파인더, ETÉREO 의 a) b) 디테일)

표지 B안과 같은 지면: 검정 바탕 · 산세리프 · 회색 단계 · 색은 사진 안에만. 빨강은 초점 원 하나에만.
사진은 사용자 것만, 자르기 · 배치만. 파일로 받지 못한 사진은 번호가 적힌 빈 칸으로 둔다(assets.md).
"""
import html
import os
import subprocess

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
PHOTO = os.path.join(REPO, 'docs/jaju_rounding_vmd/assets/photo')
OUT = os.path.join(REPO, 'docs/jaju_rounding_vmd/layout')
TMP = os.path.join(REPO, 'out/jaju_layout')
FONTS = os.path.join(REPO, 'tools/p1_layout/fonts')
PRINT = os.path.join(REPO, 'tools/p1_layout/print_pdf.mjs')
RED = '#D9362B'
e = html.escape

# assets.md 의 기록 — 파일이 없는 사진의 빈 칸에 적는다
DESC = {
    'PH-06': '원색 푸드 트럭, 메뉴판 앞에 선 사람의 등',
    'PH-08': '젖은 횡단보도, 빨간 신호등',
    'PH-09': '드럼통 꼬마 기차와 물웅덩이의 반영',
    'PH-11': '가게 앞에 앉은 노인, 지나가는 사람들',
    'PH-12': '육교 아래 곡선 도로',
    'PH-13': '틈 사이로 본 옥상의 사람들',
    'PH-15': '자전거 거치대의 반복 곡선',
    'PH-16': '파스텔 돌담과 바닥 그림',
    'PH-17': '접힌 파라솔 셋, 벤치의 두 사람',
}


def has(pid):
    return os.path.exists(os.path.join(PHOTO, pid + '.jpg'))


def size(pid):
    return Image.open(os.path.join(PHOTO, pid + '.jpg')).size


def div(x, y, w, h, inner='', cls='', style=''):
    return f"<div class='{cls}' style='left:{x}mm;top:{y}mm;width:{w}mm;height:{h}mm;{style}'>{inner}</div>"


def photo(pid, x, y, w, h, focus=(0.5, 0.5), zoom=1.0, marks=''):
    """틀을 사진으로 채운다. focus = 원본에서 틀 가운데에 올 점(0–1). zoom > 1 이면 더 가까이.
    marks(px 좌표 → mm 로 바꾸는 함수를 받는 콜백 결과)는 사진 위에 SVG 로 얹는다. 파일이 없으면 번호가 적힌 빈 칸."""
    if not has(pid):
        return div(x, y, w, h, f"<div class='phid'>{pid}</div><div class='phd'>{e(DESC.get(pid, ''))}</div><div class='phw'>파일 대기</div>", 'slot')
    W, H = size(pid)
    s = max(w / W, h / H) * zoom
    iw, ih = W * s, H * s
    ox = min(0, max(w - iw, w / 2 - focus[0] * iw))
    oy = min(0, max(h - ih, h / 2 - focus[1] * ih))
    to = lambda px, py: (ox + px * s, oy + py * s)
    svg = marks(to, s) if callable(marks) else ''
    src = 'file://' + os.path.join(PHOTO, pid + '.jpg')
    return div(x, y, w, h, f"<img src='{src}' style='left:{ox:.3f}mm;top:{oy:.3f}mm;width:{iw:.3f}mm;height:{ih:.3f}mm'>"
               + (f"<svg class='ov' viewBox='0 0 {w} {h}'>{svg}</svg>" if svg else ''), 'ph')


def t(x, y, w, h, inner, cls, style=''):
    return div(x, y, w, h, inner, 't ' + cls, style)


def corners(w, h, l=7, inset=3):
    """뷰파인더의 네 모서리."""
    a, b, c, d = inset, inset, w - inset, h - inset
    p = [f'M{a},{b + l}V{b}H{a + l}', f'M{c - l},{b}H{c}V{b + l}', f'M{a},{d - l}V{d}H{a + l}', f'M{c - l},{d}H{c}V{d - l}']
    return ''.join(f"<path d='{q}' class='cn'/>" for q in p)


def focal(cx, cy, r=4.2, label='', lx=None, ly=None, anchor='start'):
    o = f"<circle cx='{cx:.2f}' cy='{cy:.2f}' r='{r}' class='fc'/>"
    if label:
        o += f"<text x='{lx:.2f}' y='{ly:.2f}' text-anchor='{anchor}' class='lb'>{e(label)}</text>"
    return o


def dash(x, y, w, h):
    return f"<rect x='{x:.2f}' y='{y:.2f}' width='{w:.2f}' height='{h:.2f}' class='ds'/>"


def head(n, label):
    return (t(10, 7, 80, 4, 'FROM THE INSIDE', 'tiny') + t(207, 7, 80, 4, f'{n:02d}', 'tiny r')
            + t(10, 201, 120, 4, label, 'tiny'))


# ── 2쪽 · 여는 면 ───────────────────────────────────────────────────────────────────
def page2():
    def m(to, s):
        return corners(178, 148)
    return ''.join([
        head(2, '01 — OBSERVE'),
        t(18, 54, 80, 30, '01', 'chno'),
        t(18, 92, 90, 12, 'Observe', 'chtitle'),
        t(18, 105, 90, 8, '관찰하다', 'chko'),
        t(18, 124, 82, 30, '<p>나는 사람들이 어디에서 걸음을 멈추는지 본다.</p>'
                           '<p>멈춘 자리에는 늘 무언가가 놓여 있었다.</p>', 'body'),
        t(18, 141, 82, 20, '<p>I watch where people stop.</p><p>There was always something in front of them.</p>', 'bodyen'),
        photo('PH-04', 109, 31, 178, 148, focus=(0.55, 0.55), marks=m),
        t(109, 182, 178, 5, '<b>PH-04</b>&nbsp;&nbsp;고르는 사람들의 등 &nbsp;·&nbsp; 메뉴 앞에서', 'cap'),
    ])


# ── 3쪽 · 격자 ─────────────────────────────────────────────────────────────────────
GRID = [  # 사람이 멈춘다 → 모인다 · 되풀이된다 → 색과 선이 이어진다
    ('PH-06', 'Stop', (0.3, 0.6)), ('PH-11', 'Pause', (0.5, 0.5)), ('PH-17', 'Rest', (0.37, 0.6)),
    ('PH-01', 'Gather', (0.4, 0.62)), ('PH-03', 'Rhythm', (0.3, 0.55)), ('PH-09', 'Repeat', (0.6, 0.6)),
    ('PH-15', 'Line', (0.5, 0.6)), ('PH-16', 'Colour', (0.4, 0.6)), ('PH-12', 'Flow', (0.5, 0.6)),
]


def page3():
    gx, gy, cw, gap = 100, 31, 59.5, 4.25
    ch = cw * 9 / 16
    cells = []
    for i, (pid, word, f) in enumerate(GRID):
        r, c = divmod(i, 3)
        x, y = gx + c * (cw + gap), gy + r * (ch + 12)
        cells.append(photo(pid, x, y, cw, ch, focus=f))
        cells.append(t(x, y + ch + 1.8, cw, 4, f"<b>{i + 1:02d}</b>&nbsp;&nbsp;{word}<span class='pid'>{pid}</span>", 'gcap'))
    return ''.join([
        head(3, '01 — OBSERVE'),
        t(18, 31, 72, 6, 'Where people stop', 'h'),
        t(18, 40, 72, 40, '<p>멈춘 자리를 모아 보면</p><p>사람이 모이고, 같은 것이 되풀이되고,</p><p>색과 선이 이어진다.</p>', 'body'),
        t(18, 62, 70, 20, '<p>Where people stop, they gather.</p><p>Things repeat. Colours and lines carry on.</p>', 'bodyen'),
        t(18, 150, 70, 30, '<p><b>Stop · Pause · Rest</b>&nbsp; 멈춘 사람</p><p><b>Gather · Rhythm · Repeat</b>&nbsp; 모이고 되풀이됨</p>'
                           '<p><b>Line · Colour · Flow</b>&nbsp; 이어지는 선과 색</p>', 'key'),
        *cells,
    ])


# ── 4쪽 · 디테일 ───────────────────────────────────────────────────────────────────
def page4():
    def big(to, s):  # PH-05: 넓은 바다에서 눈이 먼저 가는 곳 — 모서리의 빨간 의자
        cx, cy = to(1072, 578)
        return (dash(6, 6, 178 - 12, 100 - 22) + f"<text x='8' y='10.5' class='lb'>바다 · 사람 · 하늘</text>"
                + focal(cx, cy, 5) + f"<line x1='{cx - 5.5:.1f}' y1='{cy - 2:.1f}' x2='{cx - 16:.1f}' y2='{cy - 2:.1f}' class='gl'/>"
                + f"<text x='{cx - 17:.1f}' y='{cy - 1.1:.1f}' text-anchor='end' class='lb'>a)  Red chair</text>")

    def pink(to, s):  # PH-01: 수십 명 가운데 한 사람
        cx, cy = to(687, 545)
        return focal(cx, cy, 4.2, 'b)  Pink', cx + 6, cy + 1)

    def signal(to, s):  # PH-08: 어둠 속 빨간 신호 둘 — 가까운 쪽에 초점
        cx, cy = to(880, 94)
        return focal(cx, cy, 3.6, 'c)', cx + 5, cy + 1)

    def gap(to, s):  # PH-13: 벽 틈이 만든 틀 — 그 안의 사람들에 점선 틀
        x0, y0 = to(390, 230)
        return dash(x0, y0, 950 * s, 300 * s) + f"<text x='{x0 + 1:.1f}' y='{y0 - 1.5:.1f}' class='lb'>d)</text>"

    return ''.join([
        head(4, '01 — OBSERVE'),
        t(18, 31, 72, 6, 'What made me stop', 'h'),
        t(18, 40, 74, 40, '<p>넓은 장면에서도 눈은 한 점에 먼저 간다.</p><p>빨간 의자, 분홍 수영복, 빨간 신호,</p><p>틈 사이의 불빛.</p>', 'body'),
        t(18, 62, 72, 20, '<p>In a wide scene, the eye goes to one point first.</p>', 'bodyen'),
        t(18, 92, 72, 46,
          "<div class='k'><b>a)</b> Red chair<span>파란 바다 · 모서리의 빨강</span></div>"
          "<div class='k'><b>b)</b> Pink<span>수십 명 가운데 한 사람</span></div>"
          "<div class='k'><b>c)</b> Signal<span>어둠 속 빨간 신호</span></div>"
          "<div class='k'><b>d)</b> Through the gap<span>틈 너머의 사람들</span></div>", 'keys'),
        t(18, 160, 86, 20, '<p>진열도 같다. 시선이 먼저 닿을 한 점을 정하고, 그 점이 놓일 자리를 만든다.</p>', 'bridge'),
        photo('PH-05', 109, 31, 178, 100, focus=(0.5, 0.5), marks=big),
        photo('PH-01', 109, 136, 57, 44, focus=(0.458, 0.64), zoom=3.0, marks=pink),
        photo('PH-08', 169.5, 136, 57, 44, focus=(0.62, 0.3), zoom=1.6, marks=signal),
        photo('PH-13', 230, 136, 57, 44, marks=gap),
        t(169.5, 181, 57, 4, 'c)  Signal', 'gcap'), t(230, 181, 57, 4, 'd)  Through the gap', 'gcap'),
        t(109, 181, 57, 4, 'b)  Pink — PH-01 확대', 'gcap'),
    ])


def font(f):
    return 'file://' + os.path.join(FONTS, f)


CSS = f"""
@font-face{{font-family:Inst;src:url('{font('InstrumentSans-Regular.ttf')}')}}
@font-face{{font-family:Inst;font-weight:700;src:url('{font('InstrumentSans-Bold.ttf')}')}}
@page{{size:297mm 210mm;margin:0}}*{{box-sizing:border-box;margin:0;padding:0}}html,body{{background:#555}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;font-family:Inst,'WenQuanYi Zen Hei',sans-serif}}
.sheet{{position:relative;width:297mm;height:210mm;overflow:hidden;page-break-after:always;background:#0B0B0B;color:#CFCFCF}}
.sheet div{{position:absolute}}.t p{{white-space:nowrap}}.r{{text-align:right}}
.ph{{overflow:hidden;background:#151515}}.ph img{{position:absolute;display:block}}
.ov{{position:absolute;inset:0;width:100%;height:100%;overflow:visible}}
.ov .cn{{fill:none;stroke:#fff;stroke-width:.45}}.ov .ds{{fill:none;stroke:#fff;stroke-width:.3;stroke-dasharray:1.4 1}}
.ov .fc{{fill:none;stroke:{RED};stroke-width:.55}}.ov .gl{{stroke:#fff;stroke-width:.2;stroke-dasharray:.8 .8}}
.ov .lb{{font-family:Inst,'WenQuanYi Zen Hei',sans-serif;font-size:2.5px;fill:#fff}}
.slot{{background:#161616;outline:.25mm dashed #4a4a4a;outline-offset:-.25mm}}
.slot div{{position:absolute;left:2.5mm;right:2.5mm}}.phid{{top:2.2mm;font-size:7pt;font-weight:700;color:#8a8a8a}}
.phd{{top:6.6mm;font-size:5.6pt;line-height:1.35;color:#6f6f6f}}.phw{{bottom:2mm;font-size:5.2pt;color:{RED}}}
.tiny{{font-size:6pt;line-height:8pt;letter-spacing:.06em;color:#8a8a8a;white-space:nowrap}}
.chno{{font-size:64pt;line-height:64pt;font-weight:700;color:#fff;letter-spacing:-.02em}}
.chtitle{{font-size:22pt;line-height:26pt;font-weight:700;color:#fff}}.chko{{font-size:10pt;color:#8a8a8a}}
.h{{font-size:9pt;line-height:12pt;font-weight:700;color:#fff}}
.body{{font-size:9.6pt;line-height:16pt;color:#CFCFCF}}.bodyen{{font-size:7pt;line-height:10.5pt;color:#8a8a8a}}
.cap,.gcap{{font-size:6pt;line-height:8pt;color:#8a8a8a;white-space:nowrap}}.cap b,.gcap b{{color:#fff}}
.gcap .pid{{float:right;color:#555}}
.key{{font-size:6.6pt;line-height:12pt;color:#8a8a8a}}.key b{{color:#CFCFCF}}
.keys .k{{position:static;font-size:8pt;line-height:11pt;color:#fff;margin-bottom:3mm}}.keys .k b{{color:{RED};margin-right:1.5mm}}
.keys .k span{{display:block;font-size:6.4pt;color:#8a8a8a;padding-left:5mm}}
.bridge{{font-size:7.6pt;line-height:12pt;color:#fff;border-top:.2mm solid #444;padding-top:2.5mm}}.bridge p{{white-space:normal}}
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    body = ''.join(f"<div class='sheet'>{p()}</div>" for p in (page2, page3, page4))
    h = os.path.join(TMP, 'ch1_photo.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU ch1 photo</title><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'ch1_photo.pdf'), os.path.join(TMP, 'ch1_photo')], check=True)


if __name__ == '__main__':
    main()
