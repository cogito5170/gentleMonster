"""JAJU 포트폴리오 — B4: B3 를 b3_gap_analysis.md 대로 고친 판 (새 사진 없이 할 수 있는 만큼).

  python3 tools/jaju_layout/plan_b4.py   ->  docs/jaju_rounding_vmd/layout/plan_b4.pdf

B3 에서 바꾼 것:
  패션 파트 보강     새 쪽 11 Items — 가진 착장 사진에서 아이템을 잘라 사물 초상처럼(VERLAG V3/V5). 색은 그 자리에서 잰 값
                    10 Four places 의 팔레트를 고른 값이 아니라 착장 사진에서 잰 값으로
  제안을 실제 물건으로 13 Proposal 의 칸을 내 옷 · 모형 속 생활 물건으로 (새싹 · 방파제 벽을 뺐다)
  자기 소개           새 쪽 15 About — 이름 · 전공 · 지원 · 재료 · 빈칸(학교 · 경험 · 연락처) · 이미지 출처 칸
  실 한 가닥          파트 1 을 틈 너머의 사진(PH-13)으로 연다 — '안에서 밖을 본다'와 같은 시선. 04 의 d) 는 난간 너머(PH-07)로
  사진 톤             파트 1 사진에 한 가지 보정(채도 조금 낮게 · 따뜻하게), 원본은 그대로
지어내지 않는다: 아이템 이름은 사진에서 보이는 것, 색은 픽셀에서 잰 값, 모르는 사실은 ____.
"""
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b3 as b3  # noqa: E402  (pe 의 색 · 쪽 부품을 B3 톤으로)

pe = b3.pe
pc, t, div, photo, e, af, frame = pe.pc, pe.t, pe.div, pe.photo, pe.e, pe.af, pe.frame
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT
RAW = b3._foot  # plan_e 의 원래 바닥 줄

# plan_e 쪽 함수가 부르는 번호 → 이 책의 번호
MAP = {5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 12, 11: 13, 12: 14}
pe.foot = lambda n, part='': RAW(MAP.get(n, n), part)


# ── 도구: 원본 픽셀 영역으로 자르기 · 그 영역의 평균색 ─────────────────────────────────────
CROPS = os.path.join(TMP, 'crops')


def crop(pid, x, y, w, h, cx, cy, span, marks=None):
    """원본 (cx, cy) 를 가운데로 가로 span px 을 잘라 작은 파일로 만들어 넣는다(PDF 를 가볍게)."""
    im = Image.open(pc.path(pid)).convert('RGB')
    W, H = im.size
    sh = span * h / w
    l, tp = max(0, min(W - span, cx - span / 2)), max(0, min(H - sh, cy - sh / 2))
    c = im.crop((int(l), int(tp), int(l + span), int(tp + sh)))
    c.thumbnail((900, 900))
    os.makedirs(CROPS, exist_ok=True)
    f = os.path.join(CROPS, f'{pid}_{cx}_{cy}_{span}.jpg')
    c.save(f, quality=84)
    return div(x, y, w, h, f"<img src='file://{f}' style='left:0;top:0;width:{w}mm;height:{h}mm;object-fit:cover'>", 'ph')


def mean_hex(pid, box):
    im = Image.open(pc.path(pid)).convert('RGB').crop(box)
    im = im.resize((40, 40))
    px = list(im.getdata())
    r, g, b = (sum(p[i] for p in px) // len(px) for i in range(3))
    return f'#{r:02X}{g:02X}{b:02X}'


# ── 02 · Observe — 틈 너머로 연다 ───────────────────────────────────────────────────────
def p_observe():
    return pe.part_open(2, 1, 'Observe', 'PH-13', (0.5, 0.4), '틈 너머로, 사람들이 멈춘 자리를 본다.',
                        'Through the gap, I watch where people stop.')


# ── 04 · What made me stop — d) 를 난간 너머로 ──────────────────────────────────────────
def p_detail():
    def chair(to, s):
        cx, cy = to(1072, 578)
        return af(cx, cy, 6.5, f'a)  {pe.accent("PH-05")}', 'left') + frame(6, 6, 166, 76, 'WIDE')

    def pink(to, s):
        cx, cy = to(687, 545)
        return af(cx, cy, 4, 'b)')

    def sig(to, s):
        cx, cy = to(880, 94)
        return af(cx, cy, 3.4, 'c)')

    def rail(to, s):
        x0, y0 = to(300, 60)
        fx, fy = to(707, 600)
        return frame(x0, y0, 400 * s, 640 * s, 'd)') + af(fx, fy, 2.6)

    keys = ''.join(f"<div class='k'><b>{a}</b> {b}<span>{c}</span></div>" for a, b, c in
                   [('a)', 'Red chair', '파란 바다, 모서리의 빨강'), ('b)', 'Pink', '수십 명 가운데 한 사람'),
                    ('c)', 'Signal', '어둠 속 빨간 신호'), ('d)', 'Through the rail', '난간 너머, 불 앞에 선 사람의 등')])
    return ''.join([
        t(14, 22, 84, 10, 'What made me stop', 'h2'),
        t(14, 36, 84, 30, '<p>넓은 장면에서도 눈은 한 점에 먼저 간다.</p>', 'kb'),
        t(14, 60, 84, 60, keys, 'keys'),
        t(14, 150, 84, 30, '<p>진열도 같다.</p><p>시선이 먼저 닿을 한 점을 정하고,</p><p>그 점이 놓일 자리를 만든다.</p>', 'kbb'),
        photo('PH-05', 109, 22, 178, 100, focus=(0.5, 0.5), marks=chair),
        photo('PH-01', 109, 128, 57, 50, focus=(0.458, 0.64), zoom=3.0, marks=pink),
        photo('PH-08', 169.5, 128, 57, 50, focus=(0.6, 0.2), zoom=1.6, marks=sig),
        photo('PH-07', 230, 128, 57, 50, focus=(0.33, 0.45), marks=rail),
        RAW(4, 'PART 1 OBSERVE'),
    ])


# ── 10 · Four places — 팔레트를 잰 값으로 ────────────────────────────────────────────────
OUTFITS = [  # (pid, 옷이 보이는 영역 box, 이름)
    ('FA-01', (700, 1400, 850, 1700), 'OLIVE PARKA'),
    ('FA-04', (580, 860, 720, 1100), 'BLACK COAT'),
    ('FA-05', (820, 1050, 900, 1200), 'BEIGE JACKET'),
    ('FA-03', (600, 650, 800, 850), 'GREY KNIT'),
]


def p_four():
    three = [('FA-04', (0.53, 0.55), '02', 'EVENING', 'SHOP FRONT'), ('FA-05', (0.72, 0.6), '03', 'AFTERNOON', 'PARK'),
             ('FA-03', (0.6, 0.5), '04', 'SUNNY', 'SEASIDE ROCKS')]
    o = [photo('FA-01', 0, 0, 148.5, 210, focus=(0.55, 0.6)),
         t(10, 192, 130, 5, 'N°01&nbsp;&nbsp;NIGHT&nbsp;&nbsp;RIVERSIDE', 'data lt'),
         t(162, 22, 122, 10, 'Four places, four outfits', 'h2'),
         t(162, 36, 122, 20, '<p>나는 그날 갈 장소에 옷의 톤을 맞춘다.</p><p>장소가 틀이라면, 옷은 그 틀을 채우는 조합이다.</p>', 'kb')]
    for i, (pid, f, n, tod, place) in enumerate(three):
        x = 162 + i * 41.5
        o.append(photo(pid, x, 64, 38.5, 56, focus=f))
        o.append(t(x, 122, 38.5, 10, f"<p>N°{n}&nbsp;&nbsp;{tod}</p><p>{place}</p>", 'data'))
    sw = ''.join(f"<div><i style='background:{h}'></i><span>{name}<br>{h}</span></div>"
                 for h, name in ((mean_hex(pid, box), name) for pid, box, name in OUTFITS))
    o += [t(162, 146, 122, 6, 'PALETTE — 착장 사진에서 잰 색', 'data'), div(162, 152, 122, 22, sw, 'pal'),
          RAW(10, 'PART 3 FILL')]
    return ''.join(o)


# ── 11 · Items — 아이템 초상 (새 쪽) ───────────────────────────────────────────────────
ITEMS = [  # pid, 가운데 (cx, cy), 보일 폭 px, 이름, 국문
    ('FA-01', (880, 1350), 520, 'OLIVE PARKA', '올리브 롱 파카'),
    ('FA-04', (650, 900), 330, 'BLACK COAT', '검정 오버핏 롱코트'),
    ('FA-03', (650, 760), 360, 'GREY KNIT', '회색 니트'),
    ('FA-02', (230, 610), 260, 'WHITE SHIRT · WATCH', '흰 셔츠 · 시계'),
    ('FA-05', (860, 1100), 260, 'BEIGE JACKET', '베이지 재킷'),
    ('FA-04', (605, 1440), 200, 'GREY SNEAKERS', '회색 스니커즈'),
]


def p_items():
    o = [t(14, 22, 84, 10, 'Items', 'h2'),
         t(14, 36, 84, 40, '<p>조합은 아이템에서 시작한다.</p><p>자주 입는 여섯 가지를</p><p>진열하듯 하나씩 놓았다.</p>', 'kb'),
         t(14, 74, 82, 20, 'A combination starts from items. Six things I wear often, set out one by one.', 'enb wrap'),
         t(14, 160, 84, 26, '<p>사진: 착장 사진(FA-01–05)에서 잘라 냈다.</p><p>색: 그 자리 픽셀의 평균.</p>', 'note')]
    cw, ch, gx, gy = 58, 70, 106, 22
    for i, (pid, (cx, cy), span, en, ko) in enumerate(ITEMS):
        r, c = divmod(i, 3)
        x, y = gx + c * (cw + 3.5), gy + r * (ch + 14)
        half = span / 2
        hx = mean_hex(pid, (int(cx - half / 2), int(cy - half / 2), int(cx + half / 2), int(cy + half / 2)))
        o.append(crop(pid, x, y, cw, ch, cx, cy, span))
        o.append(t(x, y + ch + 1.8, cw, 10, f"<p>N°{i + 1:02d}&nbsp;&nbsp;{en}<span class='sw' style='background:{hx}'></span><span class='hx'>{hx}</span></p><p>{ko}</p>", 'data'))
    o.append(RAW(11, 'PART 3 FILL'))
    return ''.join(o)


# ── 13 · Proposal — 칸을 내 물건으로 ───────────────────────────────────────────────────
def p_proposal():
    x0, y0, cw, ch = 160, 26, 38, 40
    cells = [('AR-07', (548, 420), 220, 'Light'), None, ('FA-03', (650, 760), 360, 'Knit'),
             ('FA-02', (230, 610), 260, 'Shirt'), ('FA-04', (640, 950), 700, 'Outfit'), ('AR-07', (550, 520), 300, 'Table'),
             None, ('FA-04', (605, 1440), 200, 'Shoes'), None]
    o = [t(14, 22, 130, 14, 'Proposal', 'h1'),
         t(14, 44, 130, 20, '<p>세 파트를 한 칸에 모은다.</p><p>생활의 물건 사이, 눈높이 가운데 칸에 옷의 조합 하나.</p>', 'kb'),
         t(14, 70, 130, 50, "<div class='k'><b>01</b> Observe<span>멈추는 자리를 본다 — 눈높이 가운데</span></div>"
                            "<div class='k'><b>02</b> Contain<span>칸을 세우고, 비울 칸을 남긴다</span></div>"
                            "<div class='k'><b>03</b> Fill<span>내 옷과 생활 물건으로 채운다</span></div>", 'keys'),
         t(14, 170, 126, 16, '<p>제안 — 실제로 시공하거나 진열한 것이 아니라 구상이다. 칸 속은 이 책에 실린 내 옷과 모형 속 물건이고, 치수는 매장을 재서 정한다.</p>', 'note')]
    for i, cell in enumerate(cells):
        r, c = divmod(i, 3)
        x, y = x0 + c * cw, y0 + r * ch
        if cell:
            pid, (cx, cy), span, w = cell
            o.append(crop(pid, x + 3, y + 3, cw - 6, ch - 10, cx, cy, span))
        o.append(t(x + 3, y + ch - 6, cw - 6, 4, cell[3] if cell else 'Void', 'cell' + ('' if cell else ' void')))
    g = ''.join(f"<line x1='{x0 + c * cw}' y1='{y0}' x2='{x0 + c * cw}' y2='{y0 + 3 * ch}' class='hl'/>" for c in range(4))
    g += ''.join(f"<line x1='{x0}' y1='{y0 + r * ch}' x2='{x0 + 3 * cw}' y2='{y0 + r * ch}' class='hl'/>" for r in range(4))
    ey = y0 + ch * 1.45
    g += f"<line x1='{x0 - 8}' y1='{ey}' x2='{x0 + 3 * cw + 6}' y2='{ey}' class='hld'/><text x='{x0 - 8}' y='{ey - 1.4}' class='hlt'>EYE LEVEL</text>"
    g += f"<circle cx='{x0 + cw * 1.5}' cy='{y0 + ch + 3}' r='1.2' class='acc'/>"
    g += f"<text x='{x0}' y='{y0 + 3 * ch + 7}' class='hlt'>ELEVATION — 한 칸의 진열 (제안 · 치수 없음)</text>"
    o.append(div(0, 0, 297, 210, f"<svg class='ov' viewBox='0 0 297 210'>{g}</svg>", ''))
    o.append(RAW(13))
    return ''.join(o)


# ── 15 · About — 자기 소개 (새 쪽) ─────────────────────────────────────────────────────
def p_about():
    rows = [('NAME', pe.NAME), ('MAJOR', '건축학과 · 학교 · 학년 ____'), ('APPLYING', 'JAJU 라운딩 VMD'),
            ('EXPERIENCE', '판매 · 진열 · 매장 경험 ____'), ('ROUNDING', '출장 · 장기 근무 가능 여부 ____'),
            ('CONTACT', '전화 ____ · 이메일 ____'),
            ('IN THIS BOOK', '사진 17 · 건축 작업 10 · 착장 5 — 모두 직접 찍고 만든 것'),
            ('IMAGE CREDIT', '표지 이미지 ____ (직접 촬영 / 출처)')]
    tbl = ''.join(f"<div class='ab'><b>{a}</b><span>{b}</span></div>" for a, b in rows)
    return ''.join([
        photo('FA-05', 0, 0, 148.5, 210, focus=(0.74, 0.62), zoom=1.6),
        t(162, 22, 122, 14, 'About', 'h1'),
        t(162, 44, 122, 30, '<p>사람이 멈추는 자리를 보고,</p><p>그 자리에 맞는 조합을 세우는 사람.</p>', 'kbb'),
        t(162, 70, 122, 110, tbl, 'abt'),
        RAW(15),
    ])


CSS = b3.CSS + """
.abt .ab{position:static;display:flex;gap:4mm;border-top:.15mm solid #3a332c;padding:2.2mm 0}
.abt .ab b{flex:0 0 30mm;font-family:Mono,monospace;font-weight:400;font-size:6.4pt;letter-spacing:.1em;color:#9A8F82}
.abt .ab span{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:9pt;color:#EFE7DA}
"""

PAGES = [(lambda: b3.p_cover(), ''), (b3.p_prologue, ''), (p_observe, 'g1'), (pe.p_grid, 'g1'), (p_detail, 'g1'),
         (b3.p_reading, 'g1'), (pe.p_contain, ''), (pe.p_collage, ''), (pe.p_room, ''), (pe.p_fill, ''), (p_four, ''),
         (p_items, ''), (pe.p_breakdown, ''), (p_proposal, ''), (pe.p_often, ''), (p_about, ''),
         (lambda: b3.p_cover(flip=True), '')]


_screen = pc.screen
GRADE = {'on': False}


def graded_screen(pid):
    src = _screen(pid)
    if not GRADE['on']:
        return src
    dst = src[:-4] + '_g1.jpg'
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        from PIL import ImageEnhance
        im = Image.open(src).convert('RGB')
        im = ImageEnhance.Color(im).enhance(0.82)
        warm = Image.new('RGB', im.size, (226, 196, 160))
        im = Image.blend(im, warm, 0.07)
        im.save(dst, quality=82)
    return dst


pc.screen = graded_screen


def render(p, g):
    GRADE['on'] = (g == 'g1')
    try:
        return p()
    finally:
        GRADE['on'] = False


def main():
    os.makedirs(TMP, exist_ok=True)
    body = ''.join(f"<div class='sheet {g}'>{render(p, g)}</div>" for p, g in PAGES)
    h = os.path.join(TMP, 'plan_b4.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B4</title><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b4.pdf'), os.path.join(TMP, 'plan_b4')], check=True)


if __name__ == '__main__':
    main()
