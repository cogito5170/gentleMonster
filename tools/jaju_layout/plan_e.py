"""JAJU 포트폴리오 — 피드백 반영안 E (B2 는 그대로 두고 따로 만든다).

  python3 tools/jaju_layout/plan_e.py   ->  docs/jaju_rounding_vmd/layout/plan_e.pdf

피드백(타인, 2026-10-21) 요지와 이 안의 답:
  무드가 먼저 · 디자인과 내용을 같은 무게로 두지 않는다
      -> 쪽마다 둘 중 하나만: '사진 한쪽 | 글 다른 쪽' 또는 '사진 위 | 글 아래'. 각 파트는 사진 전면의 무드 쪽으로 연다.
  흑백의 단조로움 · 사진 색감과 안 맞음 · 따스하게
      -> 검정 대신 따뜻한 종이색(#EDE6DA) + 짙은 갈색 먹(#2A231C) + 강조 테라코타(#B0532C, JAJU 의 오렌지 쪽).
  글자를 조금 굵게, 따스하게
      -> 제목 Young Serif(굵고 둥근 세리프), 영문 본문 Lora, 데이터 글자 IBM Plex Mono. 한글은 굵기를 올렸다.
  Part 를 나누어
      -> PART 1 OBSERVE · PART 2 CONTAIN · PART 3 FILL, 바닥 줄에 파트 이름.
쪽별 피드백에 대한 답은 docs/jaju_rounding_vmd/plan_e.md.
글꼴 한계: 이 환경에 한글 글꼴이 문천역정흑 하나뿐이라 PDF 의 한글은 그 글꼴이다. 최종본은 따뜻한 한글 세리프(예: 마루 부리 · 본명조 Bold)로 바꾼다.
"""
import colorsys
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, os.path.join(REPO, 'tools/p1_layout'))

import plan_c as pc  # noqa: E402

OUT = os.path.join(REPO, 'docs/jaju_rounding_vmd/layout')
TMP = os.path.join(REPO, 'out/jaju_layout')
FONTS = os.path.join(REPO, 'tools/p1_layout/fonts')
PRINT = os.path.join(REPO, 'tools/p1_layout/print_pdf.mjs')
PAPER, INK, MUTE, ACC, CREAM = '#EDE6DA', '#2A231C', '#7D7266', '#B0532C', '#F6F0E6'
NAME = 'JEONG HYEOKJU'
t, div, photo, e = pc.t, pc.div, pc.photo, pc.e


# ── 사진에서 잰 값 (지어내지 않는다: 픽셀에서 읽은 색) ─────────────────────────────────────
def accent(pid):
    """사진에서 가장 채도 높은 부분의 평균 색 — '눈이 멈춘 색'."""
    im = Image.open(pc.path(pid)).convert('RGB')
    im.thumbnail((240, 240))
    px = list(im.get_flattened_data()) if hasattr(im, 'get_flattened_data') else list(im.getdata())
    scored = sorted(px, key=lambda p: colorsys.rgb_to_hsv(*(c / 255 for c in p))[1] * colorsys.rgb_to_hsv(*(c / 255 for c in p))[2], reverse=True)
    top = scored[:max(8, len(scored) // 40)]
    r, g, b = (sum(p[i] for p in top) // len(top) for i in range(3))
    return f'#{r:02X}{g:02X}{b:02X}'


# ── 표시 (빨간 원 대신: 카메라 초점 칸) ────────────────────────────────────────────────
def af(cx, cy, r=4.5, label='', side='right'):
    """초점 칸: 네 모서리만 있는 작은 사각형 + 가는 지시선 + 글자. 크림색."""
    l = r * 0.55
    a, b, c, d = cx - r, cy - r, cx + r, cy + r
    o = ''.join(f"<path d='{q}' class='af'/>" for q in (f'M{a},{b + l}V{b}H{a + l}', f'M{c - l},{b}H{c}V{b + l}',
                                                         f'M{a},{d - l}V{d}H{a + l}', f'M{c - l},{d}H{c}V{d - l}'))
    o += f"<circle cx='{cx:.2f}' cy='{cy:.2f}' r='.55' class='afd'/>"
    if label:
        x2 = c + 7 if side == 'right' else a - 7
        o += f"<line x1='{(c if side == 'right' else a):.2f}' y1='{cy:.2f}' x2='{x2:.2f}' y2='{cy:.2f}' class='afl'/>"
        o += f"<text x='{x2 + (1.2 if side == 'right' else -1.2):.2f}' y='{cy + .9:.2f}' text-anchor='{'start' if side == 'right' else 'end'}' class='afs'>{e(label)}</text>"
    return o


def frame(x, y, w, h, label=''):
    o = f"<rect x='{x:.2f}' y='{y:.2f}' width='{w:.2f}' height='{h:.2f}' class='afr'/>"
    if label:
        o += f"<text x='{x + 1:.2f}' y='{y - 1.3:.2f}' class='afs'>{e(label)}</text>"
    return o


def foot(n, part=''):
    return (t(14, 199, 160, 4, f"FROM THE INSIDE{('&nbsp;&nbsp;—&nbsp;&nbsp;' + part) if part else ''}", 'ft')
            + t(243, 199, 40, 4, f"{n:02d}", 'ft r'))


def foot_light(n, part=''):
    return foot(n, part).replace("class='t ft", "class='t ft lt")


# ── 0 · 표지 ──────────────────────────────────────────────────────────────────────────
def p_cover():
    return ''.join([
        photo('COVER', 0, 0, 297, 210),
        "<div class='shadeL'></div>",
        t(14, 10, 120, 5, NAME, 'mast'), t(163, 10, 120, 5, 'VISUAL MERCHANDISER PORTFOLIO&nbsp;&nbsp;2026', 'mast r'),
        t(14, 128, 200, 50, '<p>From</p><p>the Inside</p>', 'cvt'),
        t(14, 176, 220, 8, '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.', 'cvk'),
        t(14, 184.5, 220, 6, 'From the street you see the products. From inside, you see the people.', 'cve'),
    ])


# ── 1 · Prologue (사진 한쪽 | 글 다른 쪽) ─────────────────────────────────────────────────
def p_prologue():
    body = ''.join(f'<p>{e(l)}</p>' for l in pc.LEAD_KO[:-1])
    return ''.join([
        photo('COVER', 0, 0, 148.5, 210, focus=(0.76, 0.48)),
        t(162, 22, 120, 14, 'Prologue', 'h1'),
        t(162, 44, 120, 30, '<p>밖에서 보면 상품이 보이고,</p><p>안에서 보면 사람이 보인다.</p>', 'pull'),
        t(162, 78, 120, 70, body, 'kb'),
        t(162, 130, 120, 10, f'<p>{e(pc.LEAD_KO[-1])}</p>', 'kbb'),
        t(162, 148, 112, 40, f'<p>{e(pc.LEAD_EN)}</p>', 'enb'),
        t(243, 199, 40, 4, '01', 'ft r'),
    ])


# ── 파트를 여는 무드 쪽 (사진 전면) ─────────────────────────────────────────────────────
def part_open(n, num, word, pid, focus, ko, en, dark_text=False, pos=(14, 120), zoom=1.0):
    cls = 'pt dk' if dark_text else 'pt'
    shade = '' if dark_text else "<div class='shadeL'></div>"
    x, y = pos
    return ''.join([
        photo(pid, 0, 0, 297, 210, focus=focus, zoom=zoom), shade,
        t(x, y, 200, 6, f'PART {num}', cls + ' pn'),
        t(x - 1.5, y + 6, 280, 48, word, cls + ' pw'),
        t(x, y + 52, 200, 8, ko, cls + ' pk'),
        t(x, y + 60, 200, 6, en, cls + ' pe'),
        (foot(n, f'PART {num} {word.upper()}') if dark_text else foot_light(n, f'PART {num} {word.upper()}')),
    ])


def p_observe():
    return part_open(2, 1, 'Observe', 'PH-04', (0.5, 0.5), '나는 사람들이 어디에서 걸음을 멈추는지 본다.',
                     'I watch where people stop.')


# ── 3 · Where people stop (유지 + 데이터 레터링) ─────────────────────────────────────────
GRID = [('PH-06', 'DUSK'), ('PH-11', 'DAY'), ('PH-17', 'DAY'), ('PH-01', 'DUSK'), ('PH-03', 'SUNSET'),
        ('PH-09', 'OVERCAST'), ('PH-15', 'DAY'), ('PH-16', 'DAY'), ('PH-12', 'DUSK')]


def p_grid():
    gx, gy, cw, gap = 100, 22, 59.5, 4.25
    ch = cw * 9 / 16
    o = [t(14, 22, 80, 10, 'Where people stop', 'h2'),
         t(14, 36, 80, 30, '<p>멈춘 자리를 모아 보면</p><p>사람이 모이고, 같은 것이 되풀이되고,</p><p>색과 선이 이어진다.</p>', 'kb')]
    for i, (pid, tod) in enumerate(GRID):
        r, c = divmod(i, 3)
        x, y = gx + c * (cw + gap), gy + r * (ch + 13)
        hx = accent(pid)
        o.append(photo(pid, x, y, cw, ch))
        o.append(t(x, y + ch + 1.8, cw, 4, f"N°{i + 1:02d}&nbsp;&nbsp;{tod}<span class='sw' style='background:{hx}'></span><span class='hx'>{hx}</span>", 'data'))
    o.append(t(14, 148, 80, 40, "<p>17 FRAMES / 09 SHOWN</p><p>DUSK · DAY · SUNSET · OVERCAST</p><p>&nbsp;</p>"
                                "<p>EACH FRAME, ONE COLOUR —</p><p>THE POINT WHERE MY EYE STOPPED.</p>", 'letter'))
    o.append(foot(3, 'PART 1 OBSERVE'))
    return ''.join(o)


# ── 4 · What made me stop (유지 + 표시를 초점 칸으로) ──────────────────────────────────────
def p_detail():
    def chair(to, s):
        cx, cy = to(1072, 578)
        return af(cx, cy, 6.5, f'a)  {accent("PH-05")}', 'left') + frame(6, 6, 166, 76, 'WIDE')

    def pink(to, s):
        cx, cy = to(687, 545)
        return af(cx, cy, 4, 'b)')

    def sig(to, s):
        cx, cy = to(880, 94)
        return af(cx, cy, 3.4, 'c)')

    def gap(to, s):
        x0, y0 = to(390, 230)
        return frame(x0, y0, 950 * s, 300 * s, 'd)')

    keys = ''.join(f"<div class='k'><b>{a}</b> {b}<span>{c}</span></div>" for a, b, c in
                   [('a)', 'Red chair', '파란 바다, 모서리의 빨강'), ('b)', 'Pink', '수십 명 가운데 한 사람'),
                    ('c)', 'Signal', '어둠 속 빨간 신호'), ('d)', 'Through the gap', '틈 너머의 사람들')])
    return ''.join([
        t(14, 22, 84, 10, 'What made me stop', 'h2'),
        t(14, 36, 84, 30, '<p>넓은 장면에서도 눈은 한 점에 먼저 간다.</p>', 'kb'),
        t(14, 60, 84, 60, keys, 'keys'),
        t(14, 150, 84, 30, '<p>진열도 같다.</p><p>시선이 먼저 닿을 한 점을 정하고,</p><p>그 점이 놓일 자리를 만든다.</p>', 'kbb'),
        photo('PH-05', 109, 22, 178, 100, focus=(0.5, 0.5), marks=chair),
        photo('PH-01', 109, 128, 57, 50, focus=(0.458, 0.64), zoom=3.0, marks=pink),
        photo('PH-08', 169.5, 128, 57, 50, focus=(0.6, 0.2), zoom=1.6, marks=sig),
        photo('PH-13', 230, 128, 57, 50, marks=gap),
        foot(4, 'PART 1 OBSERVE'),
    ])


# ── 5 · Contain — 단어가 사진을 담는다 ─────────────────────────────────────────────────
def p_contain():
    img = 'file://' + pc.screen('AR-03')
    return ''.join([
        t(14, 20, 120, 6, 'PART 2', 'pn2'),
        f"<div class='clip' style=\"left:10mm;top:24mm;width:280mm;height:100mm;background-image:url('{img}')\">Contain</div>",
        div(14, 134, 46, 46, "<span>담</span>", 'dam'),
        t(68, 136, 110, 10, '담다', 'h2'),
        t(68, 150, 120, 30, '<p>멈춘 자리에는 늘 틀이 있었다.</p><p>무엇을 채우고 무엇을 비울지가 그 안의 하루를 정한다.</p>', 'kb'),
        t(68, 168, 120, 10, 'Where people stop, there is always a frame.', 'enb'),
        t(214, 134, 70, 40, '<p>‘담’ 안의 ㅁ 은</p><p>한옥의 마당이자</p><p>진열대의 한 칸이다.</p>', 'side'),
        t(214, 160, 70, 10, 'AR-03 — 격자 골조 모형이 글자 안에 담겼다', 'data'),
        foot(5, 'PART 2 CONTAIN'),
    ])


# ── 6 · From the city to the room (마음에 든 쪽 — 배치 유지) ────────────────────────────────
def p_collage():
    def red(to, s):
        cx, cy = to(1525, 715)
        return af(cx, cy, 4)

    def yard(to, s):
        x0, y0 = to(380, 140)
        return frame(x0, y0, 330 * s, 400 * s)

    def capt(x, y, w, ttl, txt, pid):
        return t(x, y, w, 12, f"<i class='ct'>{ttl}</i><span>{txt}</span><span class='pid'>{pid}</span>", 'cc')

    return ''.join([
        t(14, 22, 126, 10, 'From the city to the room', 'h2'),
        t(14, 36, 124, 20, '<p>도시에서 마당으로, 마당에서 길과 집으로.</p><p>틀을 좁혀 갈수록 그 안의 하루가 보인다.</p>', 'kb'),
        photo('AR-09', 14, 62, 126.5, 58, marks=red), capt(14, 122, 126.5, 'City', '도시의 광장 — 렌더', 'AR-09'),
        photo('AR-06', 14, 140, 60, 45, focus=(0.5, 0.45), marks=yard), capt(78, 168, 62, 'Courtyard', '건물 사이를 비운 마당', 'AR-06'),
        photo('AR-05', 156.5, 22, 128.5, 54, focus=(0.45, 0.5)), capt(156.5, 78, 128.5, 'Path', '두 매스를 잇는 회랑과 길', 'AR-05'),
        photo('AR-10', 156.5, 98, 60, 60), capt(156.5, 160, 60, 'House', '골목 언덕의 집', 'AR-10'),
        photo('AR-02', 222, 98, 63, 60, focus=(0.6, 0.45)), capt(222, 160, 63, 'Hollow', '도시 아래를 비운 단면', 'AR-02'),
        t(156.5, 182, 128.5, 6, '모형 · 렌더 — 건축학과 작업. 프로젝트 이름 · 학년 ____', 'data'),
        foot(6, 'PART 2 CONTAIN'),
    ])


# ── 7 · A room, set like a display (사진 위 | 글 아래 가 아니라 기존 배치 유지, 표시만 교체) ───
def p_room():
    def living(to, s):
        ey = to(0, 455)[1]
        lx, ly = to(548, 405)
        tx, ty = to(470, 480)
        return (f"<line x1='3' y1='{ey:.1f}' x2='125.5' y2='{ey:.1f}' class='afl'/><text x='4' y='{ey - 1.4:.1f}' class='afs'>a)  EYE LEVEL</text>"
                + af(lx, ly, 3.4, 'd)') + frame(tx, ty, 165 * s, 70 * s, 'c)'))

    def hood(to, s):
        cx, cy = to(627, 222)
        return af(cx, cy, 5.5, f'b)  {accent("AR-08")}')

    keys = ''.join(f"<div class='k'><b>{a}</b> {b}<span>{c}</span></div>" for a, b, c in
                   [('a)', 'Eye level', '눈이 머무는 높이'), ('b)', 'Red point', '빨간 후드 — 시선이 먼저 닿는 곳'),
                    ('c)', 'Set', '식탁 · 의자 · 책 — 한 자리의 조합'), ('d)', 'Light', '스탠드 하나의 빛')])
    return ''.join([
        t(14, 22, 126, 10, 'A room, set like a display', 'h2'),
        t(14, 36, 124, 20, '<p>방 안에도 진열이 있다. 눈높이에 무엇을 두고,</p><p>어디에 빛을 주고, 무엇을 한 자리에 모을지.</p>', 'kb'),
        t(14, 60, 126, 40, keys, 'keys'),
        photo('AR-08', 14, 112, 126.5, 72, focus=(0.55, 0.4), marks=hood),
        photo('AR-07', 156.5, 22, 128.5, 96, focus=(0.5, 0.55), marks=living),
        t(156.5, 120, 128.5, 5, 'AR-07 — 거실 · 식당 모형', 'data'),
        photo('AR-01', 156.5, 132, 62, 52, focus=(0.55, 0.45)),
        t(223, 132, 62, 52, "<p><i class='ct'>Layer</i></p><p>얇은 판을 겹쳐 쌓은 덩어리.</p><p>빛은 겹 사이로 들어온다.</p>", 'cc'),
        foot(7, 'PART 2 CONTAIN'),
    ])


# ── 8 · Fill — 무드 먼저 ──────────────────────────────────────────────────────────────
def p_fill():
    return part_open(8, 3, 'Fill', 'FA-02', (0.55, 0.32), '웃음이 머문 곳에는 늘 조합이 있었다.',
                     'Where a smile stayed, there was always a combination.', dark_text=True, pos=(176, 20))


# ── 9 · Four places, four outfits (사진 한쪽 | 글 다른 쪽) ──────────────────────────────────
def p_four():
    three = [('FA-04', (0.53, 0.55), '02', 'EVENING', 'SHOP FRONT'), ('FA-05', (0.72, 0.6), '03', 'AFTERNOON', 'PARK'),
             ('FA-03', (0.6, 0.5), '04', 'SUNNY', 'SEASIDE ROCKS')]
    o = [photo('FA-01', 0, 0, 148.5, 210, focus=(0.55, 0.6)),
         t(10, 192, 130, 5, 'N°01&nbsp;&nbsp;NIGHT&nbsp;&nbsp;RIVERSIDE&nbsp;&nbsp;— OLIVE · BLACK · WHITE', 'data lt'),
         t(162, 22, 122, 10, 'Four places, four outfits', 'h2'),
         t(162, 36, 122, 20, '<p>나는 그날 갈 장소에 옷의 톤을 맞춘다.</p><p>장소가 틀이라면, 옷은 그 틀을 채우는 조합이다.</p>', 'kb')]
    for i, (pid, f, n, tod, place) in enumerate(three):
        x = 162 + i * 41.5
        o.append(photo(pid, x, 64, 38.5, 56, focus=f))
        o.append(t(x, 122, 38.5, 10, f"<p>N°{n}&nbsp;&nbsp;{tod}</p><p>{place}</p>", 'data'))
    sw = ''.join(f"<div><i style='background:{c}'></i><span>{w}<br>{c}</span></div>" for c, w in
                 [('#1C1C1A', 'BLACK'), ('#4F4A2C', 'OLIVE'), ('#CBBFAE', 'BEIGE'), ('#8F8B84', 'GREY')])
    o += [t(162, 146, 122, 6, 'PALETTE', 'data'), div(162, 152, 122, 22, sw, 'pal'),
          foot(9, 'PART 3 FILL')]
    return ''.join(o)


# ── 10 · Breakdown — 중요한 문장을 크게 ─────────────────────────────────────────────────
def p_breakdown():
    x0, y0, w, h = 14, 0, 100, 210
    W, H = 1202, 1500
    s = max(w / W, h / H)
    ox = min(0, max(w - W * s, w / 2 - 0.53 * W * s))
    oy = min(0, max(h - H * s, h / 2 - 0.5 * H * s))
    pts = [('HAIR', '짧고 단정하게', 610, 540, 52), ('COAT', '검정 오버핏 롱코트', 640, 930, 100),
           ('TROUSERS', '네이비 와이드 팬츠', 640, 1370, 160), ('SHOES', '회색 스니커즈', 600, 1455, 186)]
    svg = ''
    for en, ko, px, py, ly in pts:
        cx, cy = x0 + ox + px * s, y0 + oy + py * s
        svg += f"<circle cx='{cx:.2f}' cy='{cy:.2f}' r='.8' class='dot'/><polyline points='{cx:.2f},{cy:.2f} 118,{ly} 124,{ly}' class='lbl'/>"
        svg += f"<text x='125.5' y='{ly + .9}' class='lbt'><tspan class='lbb'>{en}</tspan>  {ko}</text>"
    return ''.join([
        photo('FA-04', x0, y0, w, h, focus=(0.53, 0.5)),
        div(0, 0, 297, 210, f"<svg class='ov' viewBox='0 0 297 210'>{svg}</svg>", ''),
        photo('FA-03', 190, 22, 95, 92, focus=(0.6, 0.5)),
        t(170, 124, 116, 40, '<p>매장 안의 손님은</p><p>마네킹의 등을 먼저 본다.</p>', 'pull2'),
        t(170, 150, 112, 12, 'Inside the store, people meet the mannequin’s back first.', 'enb'),
        t(170, 166, 112, 20, '<p>그래서 나는 등을 먼저 입힌다 — 니트의 결, 어깨에서 떨어지는 품.</p>', 'kb'),
        foot(10, 'PART 3 FILL'),
    ])


# ── 11 · Proposal — 마감을 부드럽게: 칸마다 실제 사진의 결 ──────────────────────────────────
def p_proposal():
    x0, y0, cw, ch = 160, 26, 38, 40
    cells = [('AR-01', 'Layer', (0.55, 0.4)), (None, 'Void', None), ('AR-07', 'Light', (0.5, 0.5)),
             ('PH-16', 'Colour', (0.4, 0.6)), ('FA-04', 'Outfit', (0.53, 0.55)), ('AR-03', 'Wood', (0.6, 0.45)),
             (None, 'Void', None), ('PH-10', 'Green', (0.5, 0.5)), (None, 'Void', None)]
    o = [t(14, 22, 130, 14, 'Proposal', 'h1'),
         t(14, 44, 130, 20, '<p>세 파트를 한 칸에 모은다.</p><p>생활의 물건 사이, 눈높이 가운데 칸에 옷의 조합 하나.</p>', 'kb'),
         t(14, 70, 130, 50, "<div class='k'><b>01</b> Observe<span>멈추는 자리를 본다</span></div>"
                            "<div class='k'><b>02</b> Contain<span>틀을 세우고 비울 칸을 남긴다</span></div>"
                            "<div class='k'><b>03</b> Fill<span>눈높이 가운데 칸을 하나의 조합으로 채운다</span></div>", 'keys'),
         t(14, 170, 126, 16, '<p>제안 — 실제로 시공하거나 진열한 것이 아니라 구상이다. 칸 속 사진은 무드 예시이고, 치수는 매장을 재서 정한다.</p>', 'note')]
    for i, (pid, w, f) in enumerate(cells):
        r, c = divmod(i, 3)
        x, y = x0 + c * cw, y0 + r * ch
        if pid:
            o.append(photo(pid, x + 3, y + 3, cw - 6, ch - 10, focus=f))
        o.append(t(x + 3, y + ch - 6, cw - 6, 4, w, 'cell' + (' void' if not pid else '')))
    g = ''.join(f"<line x1='{x0 + c * cw}' y1='{y0}' x2='{x0 + c * cw}' y2='{y0 + 3 * ch}' class='hl'/>" for c in range(4))
    g += ''.join(f"<line x1='{x0}' y1='{y0 + r * ch}' x2='{x0 + 3 * cw}' y2='{y0 + r * ch}' class='hl'/>" for r in range(4))
    ey = y0 + ch * 1.45
    g += f"<line x1='{x0 - 8}' y1='{ey}' x2='{x0 + 3 * cw + 6}' y2='{ey}' class='hld'/><text x='{x0 - 8}' y='{ey - 1.4}' class='hlt'>EYE LEVEL</text>"
    g += f"<circle cx='{x0 + cw * 1.5}' cy='{y0 + ch + 3}' r='1.2' class='acc'/>"
    g += f"<text x='{x0}' y='{y0 + 3 * ch + 7}' class='hlt'>ELEVATION — 한 칸의 진열 (제안 · 치수 없음)</text>"
    o.append(div(0, 0, 297, 210, f"<svg class='ov' viewBox='0 0 297 210'>{g}</svg>", ''))
    o.append(foot(11))
    return ''.join(o)


# ── 12 · Often — 사진 위, 번호, 아래 산문 ───────────────────────────────────────────────
def p_often():
    row = [('COVER', (0.76, 0.45), 'FROM THE INSIDE'), ('PH-04', (0.6, 0.5), 'OBSERVE'), ('AR-03', (0.6, 0.5), 'CONTAIN'),
           ('AR-07', (0.5, 0.55), 'A ROOM'), ('FA-02', (0.45, 0.45), 'FILL')]
    o = []
    for i, (pid, f, w) in enumerate(row):
        x = 14 + i * 54.6
        o.append(photo(pid, x, 22, 50.6, 72, focus=f))
        o.append(t(x, 96, 50.6, 5, f"N°{i + 1:02d}&nbsp;&nbsp;{w}", 'data'))
    o += [t(14, 116, 270, 14, '자주 보고, 자주 담고, <span class=\'acc2\'>자주</span> 채운다.', 'pull3'),
          t(14, 140, 128, 50, '<p>JAJU 는 “자주 쓸수록, 최상의 삶”이라고 말한다. 진열도 자주 볼수록 정확해진다.</p>'
                              '<p>나는 매장을 돌며 자주 보고, 그 자리에 맞게 담고, 손님의 하루에 맞는 조합으로 채우는 VMD 가 되려 한다.</p>', 'prose'),
          t(156.5, 140, 128, 40, '<p>JAJU says, “the more often you use it, the better life becomes.” A display, too, becomes more precise the more often it is looked at. '
                                 'I want to be a VMD who looks often, holds each place as it is, and fills it with what fits the day.</p>', 'enb wrap'),
          foot(12)]
    return ''.join(o)


# ── 13 · 뒤표지 ───────────────────────────────────────────────────────────────────────
def p_back():
    return ''.join([
        photo('COVER', 118, 40, 61, 86, focus=(0.13, 0.42)),
        t(14, 140, 269, 14, 'Outside', 'h1 c'),
        t(14, 156, 269, 8, '이제 당신은 밖에 있다.', 'kb c'),
        t(14, 180, 269, 14, f'<p>{NAME}</p><p>Visual Merchandiser · 연락처 ____</p>', 'data c'),
    ])


def font(f):
    return 'file://' + os.path.join(FONTS, f)


CSS = f"""
@font-face{{font-family:Young;src:url('{font('YoungSerif-Regular.ttf')}')}}
@font-face{{font-family:Lora;src:url('{font('Lora-Regular.ttf')}')}}
@font-face{{font-family:Lora;font-style:italic;src:url('{font('Lora-Italic.ttf')}')}}
@font-face{{font-family:Lora;font-weight:700;src:url('{font('Lora-Bold.ttf')}')}}
@font-face{{font-family:Mono;src:url('{font('IBMPlexMono-Regular.ttf')}')}}
@font-face{{font-family:Mono;font-weight:700;src:url('{font('IBMPlexMono-Bold.ttf')}')}}
@page{{size:297mm 210mm;margin:0}}*{{box-sizing:border-box;margin:0;padding:0}}html,body{{background:#666}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;font-family:Lora,'WenQuanYi Zen Hei',serif;color:{INK}}}
.sheet{{position:relative;width:297mm;height:210mm;overflow:hidden;page-break-after:always;background:{PAPER}}}
.sheet div{{position:absolute}}.t p{{white-space:nowrap}}.r{{text-align:right}}.c{{text-align:center}}.wrap p{{white-space:normal}}
.ph{{overflow:hidden;background:#d9d0c2}}.ph img{{position:absolute;display:block}}
.ov{{position:absolute;inset:0;width:100%;height:100%;overflow:visible}}
.ov .af{{fill:none;stroke:{CREAM};stroke-width:.4}}.ov .afd{{fill:{CREAM}}}.ov .afl{{stroke:{CREAM};stroke-width:.2}}
.ov .afr{{fill:none;stroke:{CREAM};stroke-width:.3}}.ov .afs{{font-family:Mono,monospace;font-size:2.3px;fill:{CREAM};letter-spacing:.06px}}
.ov .dot{{fill:{ACC}}}.ov .lbl{{fill:none;stroke:{INK};stroke-width:.18}}.ov .lbt{{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:2.7px;fill:{INK}}}
.ov .lbb{{font-family:Mono,monospace;font-weight:700;font-size:2.5px}}
.ov .hl{{stroke:{INK};stroke-width:.15}}.ov .hld{{stroke:{ACC};stroke-width:.2;stroke-dasharray:1 .8}}.ov .hlt{{font-family:Mono,monospace;font-size:2.2px;fill:{MUTE}}}.ov .acc{{fill:{ACC}}}
.shadeL{{left:0;top:0;width:297mm;height:210mm;background:linear-gradient(to top,rgba(20,14,8,.78),rgba(20,14,8,.25) 45%,rgba(20,14,8,0) 70%)}}
.mast{{font-family:Mono,monospace;font-size:7pt;letter-spacing:.12em;color:{CREAM};white-space:nowrap}}
.cvt{{font-family:Young,serif;font-size:58pt;line-height:58pt;color:{CREAM}}}
.cvk{{font-family:'WenQuanYi Zen Hei',sans-serif;font-weight:700;font-size:14pt;color:{CREAM};white-space:nowrap}}
.cve{{font-family:Lora,serif;font-style:italic;font-size:9pt;color:#e4d9c8;white-space:nowrap}}
.h1{{font-family:Young,serif;font-size:32pt;line-height:34pt}}.h2{{font-family:Young,serif;font-size:19pt;line-height:22pt;white-space:nowrap}}
.pull{{font-family:'WenQuanYi Zen Hei',sans-serif;font-weight:700;font-size:16pt;line-height:24pt}}
.pull2{{font-family:'WenQuanYi Zen Hei',sans-serif;font-weight:700;font-size:20pt;line-height:28pt}}
.pull3{{font-family:'WenQuanYi Zen Hei',sans-serif;font-weight:700;font-size:22pt;white-space:nowrap}}.acc2{{color:{ACC}}}
.kb{{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:10pt;line-height:17pt;-webkit-text-stroke:.15pt {INK}}}
.kbb{{font-family:'WenQuanYi Zen Hei',sans-serif;font-weight:700;font-size:10.5pt;line-height:17pt}}
.enb{{font-family:Lora,serif;font-style:italic;font-size:8.6pt;line-height:13pt;color:{MUTE}}}.enb p{{white-space:normal}}
.prose{{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:10pt;line-height:18pt;-webkit-text-stroke:.15pt {INK}}}.prose p{{white-space:normal;margin-bottom:2mm}}
.ft{{font-family:Mono,monospace;font-size:6pt;letter-spacing:.1em;color:{MUTE};white-space:nowrap}}.ft.lt{{color:{CREAM}}}
.data{{font-family:Mono,monospace;font-size:6pt;letter-spacing:.06em;color:{MUTE};white-space:nowrap}}.data p{{white-space:nowrap}}.data.lt{{color:{CREAM}}}
.data .sw{{display:inline-block;width:2.2mm;height:2.2mm;margin:0 1.2mm 0 2mm;vertical-align:-.3mm}}.data .hx{{color:{INK}}}
.letter{{font-family:Mono,monospace;font-size:7.6pt;line-height:12pt;letter-spacing:.08em;color:{INK}}}
.pt{{color:{CREAM}}}.pt.dk{{color:{INK}}}
.pn{{font-family:Mono,monospace;font-size:8pt;letter-spacing:.2em;white-space:nowrap}}
.pw{{font-family:Young,serif;font-size:118pt;line-height:118pt;white-space:nowrap}}
.pk{{font-family:'WenQuanYi Zen Hei',sans-serif;font-weight:700;font-size:13pt;white-space:nowrap}}
.pe{{font-family:Lora,serif;font-style:italic;font-size:9pt;white-space:nowrap}}
.pn2{{font-family:Mono,monospace;font-size:8pt;letter-spacing:.2em;color:{MUTE}}}
.clip{{font-family:Young,serif;font-size:205pt;line-height:100mm;letter-spacing:-.02em;background-size:cover;background-position:50% 55%;
       -webkit-background-clip:text;background-clip:text;color:transparent;white-space:nowrap}}
.dam{{border:.5mm solid {INK};display:flex;align-items:center;justify-content:center}}
.dam span{{position:static;font-family:'WenQuanYi Zen Hei',sans-serif;font-weight:700;font-size:62pt;line-height:1}}
.side{{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:9.5pt;line-height:16pt;color:{MUTE}}}
.keys .k{{position:static;font-family:Lora,serif;font-size:9pt;line-height:12pt;margin-bottom:3mm}}.keys .k b{{font-family:Mono,monospace;color:{ACC};margin-right:1.6mm}}
.keys .k span{{display:block;font-family:'WenQuanYi Zen Hei',sans-serif;font-size:7.6pt;color:{MUTE};padding-left:6mm}}
.cc{{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:6.6pt;line-height:1.5;color:{MUTE}}}.cc .ct{{display:block;font-family:Young,serif;font-style:normal;font-size:12pt;color:{INK}}}
.cc span{{display:block}}.cc .pid{{font-family:Mono,monospace;font-size:5.6pt;margin-top:.6mm}}
.pal{{display:flex;gap:1.6mm}}.pal div{{position:static;flex:1}}.pal i{{display:block;height:9mm}}
.pal span{{display:block;font-family:Mono,monospace;font-size:5.6pt;color:{MUTE};margin-top:1.2mm;font-style:normal;line-height:1.5}}
.cell{{font-family:Mono,monospace;font-size:5.6pt;letter-spacing:.08em;color:{INK}}}.cell.void{{color:{MUTE}}}
.note{{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:7.4pt;line-height:12pt;color:{MUTE};border-top:.2mm solid #cbbfae;padding-top:2.5mm}}.note p{{white-space:normal}}
"""

PAGES = [p_cover, p_prologue, p_observe, p_grid, p_detail, p_contain, p_collage, p_room, p_fill, p_four, p_breakdown,
         p_proposal, p_often, p_back]


def main():
    os.makedirs(TMP, exist_ok=True)
    body = ''.join(f"<div class='sheet'>{p()}</div>" for p in PAGES)
    h = os.path.join(TMP, 'plan_e.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan E</title><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_e.pdf'), os.path.join(TMP, 'plan_e')], check=True)


if __name__ == '__main__':
    main()
