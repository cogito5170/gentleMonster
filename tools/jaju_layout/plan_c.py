"""JAJU 포트폴리오 — 새 안(C · 잡지형) 전체 지면.

  python3 tools/jaju_layout/plan_c.py   ->  docs/jaju_rounding_vmd/layout/plan_c.pdf

지금까지의 B안(검정 · Galatasaray)과 다른 안. 네 사례를 역할별로 나눠 쓴다:
  사례 3 NEA            책의 틀 — 미색 종이 · 목차 · 편집장 글 · 장마다 '도해 사이 면 → 여는 면 → 본문'
  사례 1 ETÉREO         장 안의 펼침면 종류 — 여는 면(사진 한쪽 + 빈 면의 세리프 제목) · 콜라주 · a) b) 디테일 · 끝의 ECHO
  사례 2 Galatasaray    증명 — 같은 크기 격자(10–99 표처럼), 끝에 '짓는 법'(제안의 도면)
  사례 4 Skate zine     패션 장의 아이템 라벨 · 끝을 질문 → 지금 → 선언으로
강조색은 NEA 의 초록 대신 빨강 하나 — 표지의 빨간 스카프에서 이어지는 한 점. 사진 밖에서는 선과 번호에만 쓴다.
사진은 사용자 것만, 자르기 · 배치만. 패션 사진은 아직 받지 않아 번호가 적힌 빈 칸으로 둔다.
이미지는 긴 변 2200 px · JPEG 품질 82 로 줄여 넣어 PDF 를 10 MB 아래로 맞춘다(원본은 그대로).
"""
import html
import os
import subprocess

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
OUT = os.path.join(REPO, 'docs/jaju_rounding_vmd/layout')
TMP = os.path.join(REPO, 'out/jaju_layout')
SCREEN = os.path.join(TMP, 'screen')
FONTS = os.path.join(REPO, 'tools/p1_layout/fonts')
PRINT = os.path.join(REPO, 'tools/p1_layout/print_pdf.mjs')
SRC = {
    'PH': os.path.join(REPO, 'docs/jaju_rounding_vmd/assets/photo'),
    'AR': os.path.join(REPO, 'docs/jaju_rounding_vmd/assets/arch'),
    'CV': os.path.join(REPO, 'docs/shinsegae_vmd/p1_layout/Links'),
    'FA': os.path.join(REPO, 'docs/jaju_rounding_vmd/assets/fashion'),
}
RED, INK, PAPER, MID = '#C8322B', '#1B1A18', '#ECE8E1', '#77726A'
NAME = 'JEONG HYEOKJU'
e = html.escape

LEAD_KO = [
    '사람들은 쇼윈도를 밖에서 본다. 나는 안에서 본다.',
    '안에서 보면 가게 이름은 거꾸로 읽히고, 진열은 등을 보인다.',
    '대신 유리 너머로 사람들의 얼굴이 보인다.',
    '대부분은 그냥 지나간다. 가끔 누군가 걸음을 멈추고, 들여다보고, 웃는다.',
    '나는 그 사람이 무엇을 보고 웃었는지 본다.',
    '진열의 답은 상품이 아니라 그 표정에 있기 때문이다.',
    '그래서 나는 안에서 밖을 보는 VMD가 되려 한다.',
]
LEAD_EN = ('People look at a shop window from outside. I look from inside. From inside, the shop’s name reads backwards '
           'and the display shows its back. Instead, I see faces through the glass. Most people walk past. Now and then someone '
           'stops, looks in, and smiles. I watch what made them smile. The answer to a display is in that face, not in the '
           'product. So I want to be a VMD who looks out from the inside.')


# ── 이미지 ────────────────────────────────────────────────────────────────────────────
def path(pid):
    if pid == 'COVER':
        return os.path.join(SRC['CV'], 'cover.jpg')
    return os.path.join(SRC[pid[:2]], pid + '.jpg')


def has(pid):
    return os.path.exists(path(pid))


def screen(pid):
    """화면용 사본(긴 변 2200 px)을 만들어 그 경로를 준다."""
    os.makedirs(SCREEN, exist_ok=True)
    dst = os.path.join(SCREEN, pid + '.jpg')
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(path(pid)):
        im = Image.open(path(pid)).convert('RGB')
        im.thumbnail((2200, 2200))
        im.save(dst, quality=82, optimize=True)
    return dst


def div(x, y, w, h, inner='', cls='', style=''):
    sz = (f'width:{w}mm;' if w is not None else '') + (f'height:{h}mm;' if h is not None else '')
    return f"<div class='{cls}' style='left:{x}mm;top:{y}mm;{sz}{style}'>{inner}</div>"


def t(x, y, w, h, inner, cls, style=''):
    return div(x, y, w, h, inner, 't ' + cls, style)


def photo(pid, x, y, w, h, focus=(0.5, 0.5), zoom=1.0, marks=None, grey=False):
    """틀을 사진으로 채운다. marks(to, s) 는 원본 px 좌표를 받아 SVG 를 돌려준다. 파일이 없으면 번호가 적힌 빈 칸."""
    if not has(pid):
        return div(x, y, w, h, f"<div class='phid'>{pid}</div><div class='phd'>{e(WAIT.get(pid, ''))}</div><div class='phw'>파일 대기</div>", 'slot')
    W, H = Image.open(path(pid)).size
    s = max(w / W, h / H) * zoom
    iw, ih = W * s, H * s
    ox = min(0, max(w - iw, w / 2 - focus[0] * iw))
    oy = min(0, max(h - ih, h / 2 - focus[1] * ih))
    svg = marks(lambda px, py: (ox + px * s, oy + py * s), s) if marks else ''
    img = f"<img src='file://{screen(pid)}' style='left:{ox:.3f}mm;top:{oy:.3f}mm;width:{iw:.3f}mm;height:{ih:.3f}mm{';filter:grayscale(1)' if grey else ''}'>"
    return div(x, y, w, h, img + (f"<svg class='ov' viewBox='0 0 {w} {h}'>{svg}</svg>" if svg else ''), 'ph')


# 표시 (사진 위)
def corners(w, h, l=7, i=3):
    a, b, c, d = i, i, w - i, h - i
    return ''.join(f"<path d='{q}' class='cn'/>" for q in (f'M{a},{b + l}V{b}H{a + l}', f'M{c - l},{b}H{c}V{b + l}',
                                                             f'M{a},{d - l}V{d}H{a + l}', f'M{c - l},{d}H{c}V{d - l}'))


def ring(cx, cy, r=4.2):
    return f"<circle cx='{cx:.2f}' cy='{cy:.2f}' r='{r}' class='fc'/>"


def dash(x, y, w, h):
    return f"<rect x='{x:.2f}' y='{y:.2f}' width='{w:.2f}' height='{h:.2f}' class='ds'/>"


def lab(x, y, s, anchor='start'):
    return f"<text x='{x:.2f}' y='{y:.2f}' text-anchor='{anchor}' class='lb'>{e(s)}</text>"


# ── 지면 공통 ──────────────────────────────────────────────────────────────────────────
def chrome(n, word):
    """사례 3 · 1: 머리말(왼쪽 책 이름 · 장, 오른쪽 해 · 이름) + 바깥 여백의 세로 쪽 번호."""
    return (t(12, 8, 80, 5, f"<b>FROM THE INSIDE</b>&nbsp;&nbsp;{word}", 'hd')
            + t(205, 8, 80, 5, f"2026&nbsp;&nbsp;<b>{NAME}</b>", 'hd r')
            + t(4.2, 116, 24, 4, f"<i>page</i>&nbsp;&nbsp;{n}", 'folio', 'transform:rotate(-90deg);transform-origin:0 0')
            + t(292.8, 94, 24, 4, f"<i>page</i>&nbsp;&nbsp;{n}", 'folio', 'transform:rotate(90deg);transform-origin:0 0'))


def gutter():
    return "<div class='gut'></div>"


# ── 0 · 표지 ──────────────────────────────────────────────────────────────────────────
def p_cover():
    return ''.join([
        photo('COVER', 0, 0, 297, 210, focus=(0.5, 0.5)),
        "<div class='veil'></div>",
        t(14, 12, 140, 6, f"<b>{NAME}</b>&nbsp;&nbsp;Visual Merchandiser Portfolio", 'cvs'),
        t(214, 12, 70, 6, 'JAJU 라운딩 VMD · 2026', 'cvs r'),
        t(14, 150, 200, 44, '<p>From <i>the</i></p><p>inside</p>', 'cvt'),
        t(14, 196, 200, 6, '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.', 'cvs'),
    ])


# ── 1 · 목차 (사례 3 NEA) ─────────────────────────────────────────────────────────────
TOC = [('PROLOGUE', '안에서 밖을 본다', 2), ('OBSERVE', '관찰하다 — 사진', 3), ('CONTAIN', '담다 — 건축', 7),
       ('FILL', '채우다 — 패션', 11), ('PROPOSAL', '한 칸의 진열', 15), ('OFTEN', '자주', 16)]


def p_toc():
    rows = ''.join(f"<div class='tr'><span class='tt'>{a}</span><span class='tk'>{b}</span><span class='tn'>{n}</span></div>" for a, b, n in TOC)
    return ''.join([
        chrome(1, 'CONTENTS'), gutter(),
        t(12, 22, 60, 60, f"<p><b>FROM THE INSIDE</b></p><p>Portfolio</p><p>2026</p><br><p><b>{NAME}</b></p><p>Visual Merchandiser</p><br>"
                          "<p>지원</p><p>JAJU 라운딩 VMD</p><br><p>재료</p><p>직접 찍은 사진 · 건축학과 작업 · 나의 옷</p><br><p>연락처 ____</p>", 'colo'),
        photo('COVER', 76, 22, 64.5, 86, focus=(0.18, 0.5), grey=True),
        t(76, 110, 64.5, 6, '표지의 왼쪽 — 진열의 등', 'cap'),
        t(156.5, 22, 128.5, 160, rows, 'toc'),
    ])


# ── 2 · 프롤로그 (사례 3 EDITORIALE) ───────────────────────────────────────────────────
def p_prologue():
    ko = ''.join(f'<p>{e(l)}</p>' for l in LEAD_KO)
    return ''.join([
        chrome(2, 'PROLOGUE'), gutter(),
        t(12, 22, 128, 16, 'Prologue', 'sec'),
        t(12, 50, 128, 80, ko, 'lead'),
        t(12, 132, 118, 40, f'<p>{e(LEAD_EN)}</p>', 'en'),
        photo('COVER', 156.5, 22, 128.5, 172, focus=(0.78, 0.45)),
        t(156.5, 196, 128.5, 5, '표지 — 유리 너머 웃는 얼굴', 'cap'),
    ])


# ── 장을 여는 도해 사이 면 (사례 3) ─────────────────────────────────────────────────────
def divider(n, chap, title_en, title_ko, svg, line_ko, line_en):
    return ''.join([
        chrome(n, chap), gutter(),
        t(12, 22, 60, 30, chap.split()[0], 'chn'),
        f"<svg class='dg' viewBox='0 0 297 210'>{svg}</svg>",
        t(12, 176, 120, 8, line_ko, 'dl'),
        t(12, 184, 120, 6, line_en, 'en'),
        t(156.5, 176, 128.5, 12, f"<i>{title_en}</i>&nbsp;&nbsp;<span>{title_ko}</span>", 'dt r'),
    ])


def word(x, y, en, ko, anchor='middle', big=False):
    cls = 'dwb' if big else 'dw'
    return (f"<text x='{x}' y='{y}' text-anchor='{anchor}' class='{cls}'>{en}</text>"
            f"<text x='{x}' y='{y + (7 if big else 5.4)}' text-anchor='{anchor}' class='dk'>{ko}</text>")


def d_observe():  # 삼각형: 사람 · 멈춤 · 진열, 가운데 관찰 (NEA 의 RITRATTO · VOCE · IMPERMANENZA)
    A, B, C = (148.5, 40), (62, 140), (235, 140)
    o = f"<polygon points='{A[0]},{A[1]} {B[0]},{B[1]} {C[0]},{C[1]}' class='ln'/>"
    o += f"<circle cx='148.5' cy='106' r='14' class='lnd'/>"
    o += word(148.5, 32, 'Display', '진열') + word(56, 150, 'People', '사람', 'end') + word(241, 150, 'Stop', '멈춤', 'start')
    o += word(148.5, 105, '<tspan>Observe</tspan>', '관찰', big=True)
    o += f"<circle cx='148.5' cy='40' r='1.6' class='dot'/>"
    return divider(3, '01 OBSERVE', 'Observe', '관찰하다', o,
                   '진열과 사람 사이에서, 걸음이 멈추는 자리를 본다.', 'Between the display and the people, I look for where steps stop.')


def d_contain():  # 틀 → 비움 → 채움
    o = ''
    xs = [74, 148.5, 223]
    for i, x in enumerate(xs):
        cls = 'lnd' if i == 1 else 'ln'
        o += f"<rect x='{x - 22}' y='78' width='44' height='44' class='{cls}'/>"
        if i == 2:
            o += f"<rect x='{x - 15}' y='85' width='30' height='30' class='fillr'/>"
    for a, b in ((0, 1), (1, 2)):
        x1, x2 = xs[a] + 26, xs[b] - 26
        o += f"<line x1='{x1}' y1='100' x2='{x2}' y2='100' class='ln'/><path d='M{x2 - 3},98 L{x2},100 L{x2 - 3},102' class='ln'/>"
    o += word(74, 136, 'Frame', '틀') + word(148.5, 136, 'Void', '비움') + word(223, 136, 'Fill', '채움')
    o += "<line x1='40' y1='60' x2='257' y2='60' class='lnd'/>" + word(148.5, 54, 'Courtyard', '마당 — 비워서 삶을 담는 자리')
    return divider(7, '02 CONTAIN', 'Contain', '담다', o,
                   '멈춘 자리에는 늘 틀이 있었다. 무엇을 비우고 채울지가 그 안의 하루를 정한다.', 'Where people stop, there is always a frame.')


def d_fill():  # 작은 따옴표: 읽다 → 고르다 → 채우다
    o = "<text x='52' y='122' class='qt'>‘</text><text x='232' y='122' class='qt'>’</text>"
    o += "<rect x='86' y='72' width='125' height='56' class='lnd'/>"
    xs = [104, 148.5, 193]
    for x in xs:
        o += f"<circle cx='{x}' cy='100' r='2' class='{'dotr' if x == 193 else 'dot'}'/>"
    o += "<line x1='108' y1='100' x2='144' y2='100' class='ln'/><line x1='153' y1='100' x2='189' y2='100' class='ln'/>"
    o += word(104, 115, 'Read', '읽다') + word(148.5, 115, 'Choose', '고르다') + word(193, 115, 'Fill', '채우다')
    return divider(11, '03 FILL', 'Fill', '채우다', o,
                   '웃음이 머문 곳에는 늘 조합이 있었다. 읽은 것으로 빈 자리를 채운다.', 'Where a smile stayed, there was always a combination.')


# ── 장의 여는 면 (사례 3 · 1: 한쪽 사진, 다른 쪽 넓게 빈 면의 제목) ───────────────────────────
def opener(n, chap, pid, focus, num, en, ko, s1, s2, cap, marks=None):
    return ''.join([
        chrome(n, chap), gutter(),
        photo(pid, 12, 22, 128.5, 172, focus=focus, marks=marks),
        t(12, 196, 128.5, 5, cap, 'cap'),
        t(156.5, 22, 128.5, 10, num, 'num'),
        t(156.5, 110, 128.5, 40, f'<p>{en}</p>', 'ttl'),
        t(156.5, 146, 128.5, 6, ko, 'ttk'),
        t(156.5, 166, 120, 30, f'<p>{s1}</p><p>{s2}</p>', 'body'),
    ])


# ── 장 1 · 관찰하다 ────────────────────────────────────────────────────────────────────
def c1_open():
    return opener(4, '01 OBSERVE', 'PH-04', (0.6, 0.5), '01 / 03', 'Observe', '관찰하다',
                  '나는 사람들이 어디에서 걸음을 멈추는지 본다.', '멈춘 자리에는 늘 무언가가 놓여 있었다.',
                  'PH-04 — 메뉴 앞, 고르는 사람들의 등', marks=lambda to, s: corners(128.5, 172))


GRID = [('PH-06', 'Stop'), ('PH-11', 'Pause'), ('PH-17', 'Rest'), ('PH-01', 'Gather'), ('PH-03', 'Rhythm'),
        ('PH-09', 'Repeat'), ('PH-15', 'Line'), ('PH-16', 'Colour'), ('PH-12', 'Flow')]


def c1_grid():  # 사례 2: 같은 크기 격자로 증명
    o = [chrome(5, '01 OBSERVE'), gutter(),
         t(12, 22, 128, 8, 'Where people stop', 'h'),
         t(12, 34, 120, 30, '<p>멈춘 자리를 모아 보면 사람이 모이고,</p><p>같은 것이 되풀이되고, 색과 선이 이어진다.</p>', 'body'),
         t(12, 52, 120, 10, 'Where people stop, they gather. Things repeat. Colours and lines carry on.', 'en')]
    cw, ch, g = 39.5, 39.5 * 9 / 16, 5
    for i, (pid, w) in enumerate(GRID):
        r, cc = divmod(i, 3)
        x0 = 12 if i < 3 else 156.5
        if i < 3:
            x, y = 12 + cc * (cw + g), 120
        else:
            j = i - 3
            r, cc = divmod(j, 3)
            x, y = 156.5 + cc * (cw + g), 22 + r * (ch + 14)
        o.append(photo(pid, x, y, cw, ch))
        o.append(t(x, y + ch + 1.6, cw, 4, f"<b>{i + 1:02d}</b>&nbsp;{w}<span class='pid'>{pid}</span>", 'gc'))
    o.append(t(12, 162, 128, 20, '<p><b>01–03</b> 멈춘 사람 &nbsp; <b>04–06</b> 모이고 되풀이됨 &nbsp; <b>07–09</b> 이어지는 선과 색</p>', 'key'))
    o.append(t(156.5, 22 + 2 * (ch + 14) + ch + 10, 128.5, 6, '아홉 장 모두 같은 크기 — 고르지 않고 나란히 놓는다', 'cap'))
    return ''.join(o)


def c1_detail():  # 사례 1 DETAIL: a) b) 표시
    def chair(to, s):
        cx, cy = to(1072, 578)
        return corners(128.5, 120) + ring(cx, cy, 5) + lab(cx - 7, cy - 6, 'a)', 'end')

    def pink(to, s):
        cx, cy = to(687, 545)
        return ring(cx, cy, 3.6) + lab(cx + 5, cy + 1, 'b)')

    def sig(to, s):
        cx, cy = to(880, 94)
        return ring(cx, cy, 3.2) + lab(cx + 4.5, cy + 1, 'c)')

    def gap(to, s):
        x0, y0 = to(390, 230)
        return dash(x0, y0, 950 * s, 300 * s) + lab(x0 + 1, y0 - 1.5, 'd)')

    keys = ''.join(f"<div class='k'><b>{a}</b> {b}<span>{c}</span></div>" for a, b, c in
                   [('a)', 'Red chair', '파란 바다, 모서리의 빨강'), ('b)', 'Pink', '수십 명 가운데 한 사람'),
                    ('c)', 'Signal', '어둠 속 빨간 신호'), ('d)', 'Through the gap', '틈 너머의 사람들')])
    return ''.join([
        chrome(6, '01 OBSERVE'), gutter(),
        photo('PH-05', 12, 22, 128.5, 120, focus=(0.6, 0.5), marks=chair),
        t(12, 146, 128, 8, 'What made me stop', 'h'),
        t(12, 156, 128, 20, '<p>넓은 장면에서도 눈은 한 점에 먼저 간다.</p><p>진열도 같다. 시선이 먼저 닿을 한 점을 정하고, 그 점이 놓일 자리를 만든다.</p>', 'body'),
        photo('PH-01', 156.5, 22, 62, 50, focus=(0.458, 0.64), zoom=3.0, marks=pink),
        photo('PH-08', 223, 22, 62, 50, focus=(0.62, 0.3), zoom=1.6, marks=sig),
        photo('PH-13', 156.5, 80, 128.5, 72, focus=(0.55, 0.45), marks=gap),
        t(156.5, 160, 128.5, 34, keys, 'keys'),
    ])


# ── 장 2 · 담다 ───────────────────────────────────────────────────────────────────────
def c2_open():
    def m(to, s):
        fx, fy = to(1020, 560)
        vx, vy = to(790, 300)
        return (corners(128.5, 172) + dash(fx, fy, 330 * s, 230 * s) + lab(fx + 1, fy - 1.6, 'Fill')
                + dash(vx, vy, 190 * s, 150 * s) + lab(vx + 1, vy - 1.6, 'Void'))
    return opener(8, '02 CONTAIN', 'AR-03', (0.62, 0.5), '02 / 03', 'Contain', '담다',
                  '무엇을 채우고 무엇을 비울지가', '그 안의 하루를 정한다.', 'AR-03 — 격자 골조와 나무 판, 모형', marks=m)


def c2_collage():  # 사례 1 COLLAGE + 3 본문: 크기가 다른 사진을 엇갈리게, 이탤릭 캡션 제목
    def red(to, s):
        cx, cy = to(1525, 715)
        return ring(cx, cy, 3.6)

    def yard(to, s):
        x0, y0 = to(380, 140)
        return dash(x0, y0, 330 * s, 400 * s)

    def capt(x, y, w, ttl, txt, pid):
        return t(x, y, w, 12, f"<i class='ct'>{ttl}</i><span>{txt}</span><span class='pid'>{pid}</span>", 'cc')

    return ''.join([
        chrome(9, '02 CONTAIN'), gutter(),
        t(12, 22, 128, 8, 'From the city to the room', 'h'),
        t(12, 34, 124, 20, '<p>도시에서 마당으로, 마당에서 길과 집으로.</p><p>틀을 좁혀 갈수록 그 안의 하루가 보인다.</p>', 'body'),
        photo('AR-09', 12, 62, 128.5, 58, marks=red), capt(12, 122, 128.5, 'City', '도시의 광장 — 렌더', 'AR-09'),
        photo('AR-06', 12, 140, 60, 45, focus=(0.5, 0.45), marks=yard), capt(76, 168, 64, 'Courtyard', '건물 사이를 비운 마당', 'AR-06'),
        photo('AR-05', 156.5, 22, 128.5, 54, focus=(0.45, 0.5)), capt(156.5, 78, 128.5, 'Path', '두 매스를 잇는 회랑과 길', 'AR-05'),
        photo('AR-10', 156.5, 98, 60, 60), capt(156.5, 160, 60, 'House', '골목 언덕의 집', 'AR-10'),
        photo('AR-02', 222, 98, 63, 60, focus=(0.6, 0.45)), capt(222, 160, 63, 'Hollow', '도시 아래를 비운 단면', 'AR-02'),
        t(156.5, 180, 128.5, 6, '모형 · 렌더 — 건축학과 작업. 프로젝트 이름 · 학년 ____', 'cap'),
    ])


def c2_detail():
    def living(to, s):
        ey = to(0, 455)[1]
        lx, ly = to(548, 405)
        tx, ty = to(470, 480)
        return (corners(128.5, 96) + f"<line x1='3' y1='{ey:.1f}' x2='125.5' y2='{ey:.1f}' class='gl'/>" + lab(4, ey - 1.4, 'a)  Eye level')
                + ring(lx, ly, 3.2) + lab(lx + 4.5, ly + 1, 'd)') + dash(tx, ty, 165 * s, 70 * s) + lab(tx, ty + 70 * s + 3.6, 'c)'))

    def hood(to, s):
        cx, cy = to(627, 222)
        return ring(cx, cy, 5) + lab(cx + 6.5, cy + 1, 'b)')

    keys = ''.join(f"<div class='k'><b>{a}</b> {b}<span>{c}</span></div>" for a, b, c in
                   [('a)', 'Eye level', '눈이 머무는 높이'), ('b)', 'Red point', '빨간 후드 — 시선이 먼저 닿는 곳'),
                    ('c)', 'Set', '식탁 · 의자 · 책 — 한 자리의 조합'), ('d)', 'Light', '스탠드 하나의 빛')])
    return ''.join([
        chrome(10, '02 CONTAIN'), gutter(),
        t(12, 22, 128, 8, 'A room, set like a display', 'h'),
        t(12, 34, 124, 20, '<p>방 안에도 진열이 있다. 눈높이에 무엇을 두고,</p><p>어디에 빛을 주고, 무엇을 한 자리에 모을지.</p>', 'body'),
        t(12, 62, 128, 34, keys, 'keys'),
        photo('AR-08', 12, 112, 128.5, 72, focus=(0.55, 0.4), marks=hood),
        t(12, 186, 128.5, 5, 'AR-08 — 주방 모형', 'cap'),
        photo('AR-07', 156.5, 22, 128.5, 96, focus=(0.5, 0.55), marks=living),
        t(156.5, 120, 128.5, 5, 'AR-07 — 거실 · 식당 모형', 'cap'),
        photo('AR-01', 156.5, 132, 62, 52, focus=(0.55, 0.45)),
        t(223, 132, 62, 52, '<p><i class=\'ct\'>Layer</i></p><p>얇은 판을 겹쳐 쌓은 덩어리.</p><p>빛은 겹 사이로 들어온다.</p><span class=\'pid\'>AR-01</span>', 'cc'),
    ])


# ── 장 3 · 채우다 (패션 — 사진 받기 전, 빈 칸) ──────────────────────────────────────────
WAIT = {
    'FA-01': '착장 전신 한 장 — 가장 나다운 조합',
    'FA-02': '같은 아이템 · 다른 조합 1', 'FA-03': '같은 아이템 · 다른 조합 2',
    'FA-04': '같은 아이템 · 다른 조합 3', 'FA-05': '같은 아이템 · 다른 조합 4',
    'FA-06': '착장 한 벌 (전신, 정면)', 'FA-07': '같은 착장 뒷모습',
}


def c3_open():
    return opener(12, '03 FILL', 'FA-01', (0.5, 0.5), '03 / 03', 'Fill', '채우다',
                  '나는 자주 입는 옷으로 빈 자리를 채운다.', '같은 옷도 무엇과 함께 놓느냐에 따라 다른 하루가 된다.',
                  'FA-01 — 착장 · ____')


def c3_combos():  # 사례 2 색 변주 타일 2×2 — 같은 아이템, 다른 조합
    o = [chrome(13, '03 FILL'), gutter(),
         t(12, 22, 128, 8, 'One item, four days', 'h'),
         t(12, 34, 124, 30, '<p>한 벌을 사면 한 번 입는 것이 아니다.</p><p>자주 입을수록 조합이 늘어난다 — "자주 쓸수록".</p>', 'body'),
         t(12, 60, 124, 10, 'The more often it is worn, the more combinations it makes.', 'en'),
         t(12, 160, 128, 24, '<p><b>같은 것</b> &nbsp;____ (반복되는 아이템)</p><p><b>바뀐 것</b> &nbsp;____ · ____ · ____</p>', 'key')]
    for i, pid in enumerate(['FA-02', 'FA-03', 'FA-04', 'FA-05']):
        r, c = divmod(i, 2)
        x, y = 156.5 + c * 66, 22 + r * 86
        o.append(photo(pid, x, y, 62.5, 80))
        o.append(t(x, y + 81.2, 62.5, 4, f"<b>0{i + 1}</b>&nbsp;Day {i + 1}<span class='pid'>{pid}</span>", 'gc'))
    return ''.join(o)


def c3_breakdown():  # 사례 4 SKATE FASHION TODAY: 아이템 라벨
    def labels():
        items = [('Hair', 30), ('Eyewear', 46), ('Coat', 80), ('Watch', 112), ('Trousers', 132), ('Shoes', 168)]
        o = ''
        for i, (w, y) in enumerate(items):
            o += f"<line x1='{100}' y1='{y}' x2='{122 if i % 2 == 0 else 116}' y2='{y}' class='gl2'/>"
            o += f"<circle cx='100' cy='{y}' r='0.9' class='dotr'/><text x='124' y='{y + 1.1}' class='lb2'>{w} — ____</text>"
        return f"<svg class='ov' viewBox='0 0 297 210'>{o}</svg>"

    bar = ''.join(f"<div class='bar' style='width:{w}%;background:{c}'></div>" for w, c in
                  [(40, '#1d1d1b'), (25, '#5b5d3e'), (20, '#c9b79a'), (15, '#8d8b86')])
    return ''.join([
        chrome(14, '03 FILL'), gutter(),
        photo('FA-06', 40, 22, 56, 172),
        div(0, 0, 297, 210, labels(), ''),
        t(12, 22, 26, 40, '<p><b>Breakdown</b></p><p>착장 한 벌을</p><p>아이템으로</p>', 'side'),
        photo('FA-07', 156.5, 22, 56, 120),
        t(156.5, 144, 56, 5, '뒤에서 — 매장 안의 손님은 등을 먼저 본다', 'cap'),
        t(220, 22, 65, 10, 'Colour ratio', 'h'),
        div(220, 34, 65, 6, bar, 'bars'),
        t(220, 42, 65, 30, '<p>검정 · 올리브 · 베이지 · 회색</p><p>비율은 착장을 받은 뒤 잰다</p>', 'cap2'),
        t(220, 120, 65, 40, '<p>무엇을 고르고 무엇을 뺐는지가</p><p>조합을 만든다.</p>', 'body'),
    ])


# ── 15 · 제안 (사례 2 의 '짓는 법' — 코드로 그린 입면) ────────────────────────────────────
def p_proposal():
    x0, y0, cw, ch = 160, 40, 38, 34
    cells = [[('Void', None), ('그릇', 'fill'), ('Void', None)],
             [('리넨', 'fill'), ('옷 · 조합', 'red'), ('컵', 'fill')],
             [('Void', None), ('바구니', 'fill'), ('Void', None)]]
    o = ''
    for r, row in enumerate(cells):
        for c, (w, k) in enumerate(row):
            x, y = x0 + c * cw, y0 + r * ch
            o += f"<rect x='{x}' y='{y}' width='{cw}' height='{ch}' class='ln'/>"
            if k:
                o += f"<rect x='{x + 8}' y='{y + 5}' width='{cw - 16}' height='{ch - 15}' class='{'fillred' if k == 'red' else 'fillg'}'/>"
            o += f"<text x='{x + cw / 2}' y='{y + ch - 3}' text-anchor='middle' class='lb2'>{w}</text>"
    ey = y0 + ch * 1.5
    o += f"<line x1='{x0 - 8}' y1='{ey}' x2='{x0 + 3 * cw + 8}' y2='{ey}' class='lnd'/><text x='{x0 + 3 * cw + 9}' y='{ey + 1}' class='lb2'>Eye level</text>"
    o += f"<circle cx='{x0 + cw * 1.5}' cy='{y0 + ch * 1.5}' r='{ch * 0.5}' class='ringr'/>"
    o += f"<line x1='{x0 - 6}' y1='{y0 + 3 * ch}' x2='{x0 + 3 * cw + 6}' y2='{y0 + 3 * ch}' class='ln'/>"
    o += f"<text x='{x0}' y='{y0 + 3 * ch + 8}' class='lb2'>Elevation — 한 칸의 진열 (제안, 치수 없음)</text>"
    steps = ''.join(f"<div class='k'><b>{a}</b> {b}<span>{c}</span></div>" for a, b, c in
                    [('01', 'Observe', '멈추는 자리를 본다 — 장 1'), ('02', 'Contain', '틀을 세우고 비울 칸을 남긴다 — 장 2'),
                     ('03', 'Fill', '눈높이 가운데 칸을 하나의 조합으로 채운다 — 장 3')])
    return ''.join([
        chrome(15, 'PROPOSAL'), gutter(),
        t(12, 22, 128, 10, 'Proposal', 'sec'),
        t(12, 44, 124, 30, '<p>세 장을 한 칸에 모은다.</p><p>JAJU 매장의 진열 한 칸 — 생활의 물건 사이에 옷의 조합 하나.</p>', 'body'),
        t(12, 74, 128, 50, steps, 'keys'),
        t(12, 160, 124, 24, '<p>제안 — 실제로 시공하거나 진열한 것이 아니라 구상이다.</p><p>칸 속 물건은 예시이고, 치수는 매장을 재서 정한다.</p>', 'note'),
        f"<svg class='dg' viewBox='0 0 297 210'>{o}</svg>",
    ])


# ── 16 · 끝 (사례 1 ECHO + 사례 4 질문 → 지금 → 선언) ───────────────────────────────────
def p_often():
    return ''.join([
        chrome(16, 'OFTEN'),
        photo('COVER', 12, 22, 70, 52, focus=(0.75, 0.45)),
        photo('PH-04', 86, 22, 54, 52),
        photo('AR-03', 12, 78, 54, 40),
        photo('AR-07', 70, 78, 70, 40),
        photo('FA-06', 12, 122, 40, 62), photo('PH-05', 56, 122, 84, 62, focus=(0.9, 0.85), zoom=2.2),
        t(156.5, 22, 128.5, 10, 'Why often?', 'h'),
        t(156.5, 34, 120, 20, '<p>"자주 쓸수록, 최상의 삶."</p><p>그렇다면 진열은 무엇을 자주 해야 할까.</p>', 'body'),
        t(156.5, 92, 130, 60, '<p>자주 보고,</p><p>자주 담고,</p><p><span class=\'red\'>자주</span> 채운다.</p>', 'big'),
        t(156.5, 160, 120, 12, 'I look often. I hold often. I fill often.', 'en'),
        t(156.5, 186, 128.5, 6, '표지 · 장 1 · 장 2 · 장 3 의 사진을 다시 모았다', 'cap'),
    ])


# ── 17 · 뒤표지 ───────────────────────────────────────────────────────────────────────
def p_back():
    return ''.join([
        div(0, 0, 297, 210, '', 'inkbg'),
        t(14, 150, 200, 30, '<p>Outside</p>', 'cvt'),
        t(14, 186, 200, 6, '이제 당신은 밖에 있다.', 'cvs'),
        t(200, 176, 85, 20, f"<p><b>{NAME}</b></p><p>Visual Merchandiser</p><p>연락처 ____</p>", 'cvs r'),
    ])


def font(f):
    return 'file://' + os.path.join(FONTS, f)


CSS = f"""
@font-face{{font-family:Crimson;src:url('{font('CrimsonPro-Regular.ttf')}')}}
@font-face{{font-family:Crimson;font-style:italic;src:url('{font('CrimsonPro-Italic.ttf')}')}}
@font-face{{font-family:Inst;src:url('{font('InstrumentSans-Regular.ttf')}')}}
@font-face{{font-family:Inst;font-weight:700;src:url('{font('InstrumentSans-Bold.ttf')}')}}
@page{{size:297mm 210mm;margin:0}}*{{box-sizing:border-box;margin:0;padding:0}}html,body{{background:#666}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;font-family:Inst,'WenQuanYi Zen Hei',sans-serif;color:{INK}}}
.sheet{{position:relative;width:297mm;height:210mm;overflow:hidden;page-break-after:always;background:{PAPER}}}
.sheet div{{position:absolute}}.t p{{white-space:nowrap}}.r{{text-align:right}}
.gut{{left:148.5mm;top:16mm;width:0;height:180mm;border-left:.15mm solid #d3cdc4}}
.ph{{overflow:hidden;background:#d8d2c8}}.ph img{{position:absolute;display:block}}
.ov{{position:absolute;inset:0;width:100%;height:100%;overflow:visible}}
.ov .cn{{fill:none;stroke:#fff;stroke-width:.45}}.ov .ds{{fill:none;stroke:#fff;stroke-width:.3;stroke-dasharray:1.4 1}}
.ov .fc{{fill:none;stroke:{RED};stroke-width:.55}}.ov .gl{{stroke:#fff;stroke-width:.25;stroke-dasharray:.8 .8}}
.ov .lb{{font-family:Inst,sans-serif;font-size:2.5px;fill:#fff}}
.ov .gl2{{stroke:{INK};stroke-width:.2}}.ov .lb2{{font-family:Inst,'WenQuanYi Zen Hei',sans-serif;font-size:2.6px;fill:{INK}}}.ov .dotr{{fill:{RED}}}
.slot{{background:#e2ddd5;outline:.25mm dashed #b8b0a4;outline-offset:-.25mm}}
.slot div{{position:absolute;left:2.5mm;right:2.5mm}}.phid{{top:2.4mm;font-size:8pt;font-weight:700;color:#8d867b}}
.phd{{top:7.4mm;font-size:6pt;line-height:1.4;color:#8d867b}}.phw{{bottom:2.2mm;font-size:5.6pt;color:{RED}}}
.hd{{font-size:6.6pt;letter-spacing:.06em;white-space:nowrap}}
.folio{{font-family:Crimson,serif;font-size:7.5pt;white-space:nowrap;color:{MID}}}
.cap{{font-size:6pt;color:{MID};white-space:nowrap}}.cap2{{font-size:6.4pt;line-height:1.5;color:{MID}}}
.h{{font-size:10pt;font-weight:700}}
.body{{font-size:9.4pt;line-height:15.5pt}}.en{{font-size:7pt;line-height:10.5pt;color:{MID}}}.en p{{white-space:normal}}
.lead{{font-size:11pt;line-height:20pt}}
.sec{{font-family:Crimson,serif;font-size:40pt;line-height:40pt}}
.num{{font-family:Crimson,serif;font-size:13pt;color:{RED}}}
.ttl{{font-family:Crimson,serif;font-size:96pt;line-height:80pt;letter-spacing:-.015em}}.ttk{{font-size:11pt;color:{MID}}}
.chn{{font-family:Crimson,serif;font-size:14pt;color:{RED}}}
.dg{{position:absolute;inset:0;width:100%;height:100%;overflow:visible}}
.dg .ln{{fill:none;stroke:{RED};stroke-width:.3}}.dg .lnd{{fill:none;stroke:{RED};stroke-width:.3;stroke-dasharray:1.6 1.2}}
.dg .dot{{fill:{INK}}}.dg .dotr{{fill:{RED}}}.dg .fillr{{fill:{RED};opacity:.85}}.dg .fillg{{fill:#cfc8bc}}.dg .fillred{{fill:{RED}}}
.dg .ringr{{fill:none;stroke:{RED};stroke-width:.4}}
.dg .dw{{font-family:Crimson,serif;font-size:7px;fill:{RED}}}.dg .dwb{{font-family:Crimson,serif;font-style:italic;font-size:11px;fill:{RED}}}
.dg .dk{{font-family:Inst,'WenQuanYi Zen Hei',sans-serif;font-size:3px;fill:{MID}}}
.dg .qt{{font-family:Crimson,serif;font-size:90px;fill:{RED}}}
.dg .lb2{{font-family:Inst,'WenQuanYi Zen Hei',sans-serif;font-size:2.7px;fill:{INK}}}
.dl{{font-size:9.4pt}}.dt{{font-family:Crimson,serif;font-size:30pt}}.dt span{{font-family:Inst,'WenQuanYi Zen Hei',sans-serif;font-size:10pt;color:{MID}}}
.toc .tr{{position:static;display:flex;align-items:baseline;border-bottom:.15mm solid #cfc8bc;padding:3.2mm 0}}
.toc .tt{{font-family:Crimson,serif;font-size:24pt;line-height:24pt;width:62mm}}.toc .tk{{font-size:8pt;color:{MID};flex:1}}
.toc .tn{{font-family:Crimson,serif;font-size:13pt;color:{RED}}}
.colo{{font-size:6.6pt;line-height:9.5pt}}
.gc{{font-size:5.8pt;color:{MID};white-space:nowrap}}.gc b{{color:{INK}}}.pid{{float:right;color:#a8a196}}
.key{{font-size:7pt;line-height:12pt;color:{MID}}}.key b{{color:{INK}}}
.keys .k{{position:static;font-size:8pt;line-height:11pt;margin-bottom:2.6mm}}.keys .k b{{color:{RED};margin-right:1.5mm}}
.keys .k span{{display:block;font-size:6.4pt;color:{MID};padding-left:5.5mm}}
.cc{{font-size:6pt;line-height:1.45;color:{MID}}}.cc .ct{{display:block;font-family:Crimson,serif;font-style:italic;font-size:11pt;color:{INK}}}.cc span{{display:block}}
.cc .pid{{display:block;float:none;margin-top:.6mm}}
.side{{font-size:7pt;line-height:11pt}}
.bars{{display:flex}}.bars .bar{{position:static;height:100%}}
.note{{font-size:7pt;line-height:11pt;color:{MID};border-top:.15mm solid #cfc8bc;padding-top:2.5mm}}
.big{{font-size:30pt;line-height:40pt;font-weight:700}}.red{{color:{RED}}}
.veil{{left:0;top:0;width:297mm;height:210mm;background:linear-gradient(to top,rgba(0,0,0,.55),rgba(0,0,0,0) 45%)}}
.cvt{{font-family:Crimson,serif;font-size:76pt;line-height:62pt;color:#fff}}.cvs{{font-size:7.6pt;color:#fff;white-space:nowrap}}
.inkbg{{background:#111}}
"""

PAGES = [p_cover, p_toc, p_prologue, d_observe, c1_open, c1_grid, c1_detail, d_contain, c2_open, c2_collage, c2_detail,
         d_fill, c3_open, c3_combos, c3_breakdown, p_proposal, p_often, p_back]


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    body = ''.join(f"<div class='sheet'>{p()}</div>" for p in PAGES)
    h = os.path.join(TMP, 'plan_c.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan C</title><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_c.pdf'), os.path.join(TMP, 'plan_c')], check=True)


if __name__ == '__main__':
    main()
