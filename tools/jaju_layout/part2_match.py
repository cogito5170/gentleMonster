"""JAJU 포트폴리오 파트 2 /02 Match. — 8–11쪽 (315 × 195). 옛 파트 3(옷 쪽 넷)을 새 파트 2 로, 새 표지의 디자인 말로 다시 만든다.

  python3 tools/jaju_layout/part2_match.py   ->  docs/jaju_rounding_vmd/layout/part2_match.pdf (4쪽: 8 · 9 · 10 · 11)

사용자: "이후 파트 2를 새로운 커버 이미지와 적합한 디자인으로 다음 페이지를 구성하라. 포트폴리오의 사례를 참고하라.
옷을 다루는 기존 파트 3를 새로운 파트 2로 새롭게 제작한다."
글: 2-2 세션 파트 2 '맞추다' 확정 스토리(사용자 지시로 보냄, 10-23) — 안에서 밖으로, 한 벌 → 아이템 → 장소.
   8 /02 Match. 표지 · 9 Front, or back? (한 벌) · 10 Selection—06. (아이템) · 11 Four places, | four outfits. (장소)
표지에서 이어 받는 말(POLITICS + PARTNERSHIPS 꼴):
  · 납작한 색 면 셋 — 파란 벽 #86A7D0 · 흰 벽 · 살구색 바닥 #E2AA88 — 과 바닥 사선. 사람(사진)은 바닥선에 선다
  · 좁은 굵은 대문자 제목(흰색 또는 먹색) · 작은 굵은 대문자 줄(자간 넓게) · 먹색 #1B1B1A 글
쪽마다 사례:
  9  표지의 방을 그대로 잇는다(파란 벽에 글, 흰 벽 앞 바닥선에 앞 · 뒤 두 벌) + 사례 6 Desjobert 의 지시선 라벨
  10 사례 5 VERLAG 번호 제목 'Selection—06.' + 사례 6 Desjobert CMF 보드(COLOR · MATERIAL · FIT) — 파란 진열 벽, 바닥선 = 선반
  11 접는 선 양쪽 제목 + 사례 1 ETÉREO 캡션(굵은 첫 낱말 + 줄표) + 사례 2 Galatasaray 색 짝 — 방 넷: 벽 = 장소에서 잰 색, 바닥 = 옷에서 잰 색
색은 모두 사진 픽셀의 평균(잰 자리는 아래 PLACE · ITEMS). MATERIAL · FIT 은 사진에 보이는 것만 쓴 눈대중이다.
"""
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cover_match as cm  # noqa: E402

REPO, FONTS, OUT, TMP, PRINT, W, H = cm.REPO, cm.FONTS, cm.OUT, cm.TMP, cm.PRINT, cm.W, cm.H
FA = os.path.join(REPO, 'docs/jaju_rounding_vmd/assets/fashion')
CROPS = os.path.join(TMP, 'part2_crops')
d = cm.d
BLUE, PEACH, INK, WHITE = '#86A7D0', '#E2AA88', '#1B1B1A', '#FFFFFF'
TOP, BOT, L, R, CX, FOLIO_Y = 11.58, 180.5, 14.0, 301.0, 157.5, 184.35
WALL_X, FLOOR_Y, DIAG_X = cm.WALL_X, cm.FLOOR_Y, cm.DIAG_X


# ── 사진 · 색 ─────────────────────────────────────────────────────────────────────────
def crop(pid, x, y, w, h, cx, cy, span):
    """원본 (cx, cy) 를 가운데로 가로 span px 을 잘라 틀 비율 그대로 넣는다. 반환: (html, px→mm 함수)."""
    im = Image.open(os.path.join(FA, pid + '.jpg')).convert('RGB')
    IW, IH = im.size
    sh = span * h / w
    lft, tp = max(0, min(IW - span, cx - span / 2)), max(0, min(IH - sh, cy - sh / 2))
    c = im.crop((int(lft), int(tp), int(lft + span), int(tp + sh)))
    c.thumbnail((1000, 1000))
    os.makedirs(CROPS, exist_ok=True)
    f = os.path.join(CROPS, f'{pid}_{cx}_{cy}_{span}_{w:.0f}x{h:.0f}.jpg')
    c.save(f, quality=86)
    k = w / span
    html = d(x, y, w, h, f"<img src='file://{f}' style='position:absolute;left:0;top:0;width:{w}mm;height:{h}mm'>", 'ph')
    return html, (lambda px, py: (x + (px - lft) * k, y + (py - tp) * k))


def mean_hex(pid, box):
    im = Image.open(os.path.join(FA, pid + '.jpg')).convert('RGB')
    IW, IH = im.size
    if all(v <= 1 for v in box):  # 비율로 준 자리
        box = (box[0] * IW, box[1] * IH, box[2] * IW, box[3] * IH)
    px = list(im.crop(tuple(int(v) for v in box)).resize((40, 40)).getdata())
    r, g, b = (sum(p[i] for p in px) // len(px) for i in range(3))
    return f'#{r:02X}{g:02X}{b:02X}'


# 아이템 — B20 Items 와 같은 자리(원본 px 가운데 · 보일 폭), 색은 가운데 span/2 사각의 평균 (B20 값과 같다)
ITEMS = [  # pid, (cx, cy), span, EN, MATERIAL, FIT
    ('FA-01', (880, 1350), 520, 'OLIVE PARKA', '매트한 직물', '오버핏 · 롱'),
    ('FA-04', (650, 900), 330, 'BLACK COAT', '도톰한 직물', '오버핏 · 롱'),
    ('FA-03', (650, 760), 360, 'GREY KNIT', '굵은 결 니트', '여유'),
    ('FA-02', (230, 610), 260, 'WHITE SHIRT · WATCH', '얇은 직물 · 시계', '여유 · 소매 걷음'),
    ('FA-05', (860, 1100), 260, 'BEIGE JACKET', '매끈한 직물', '여유 · 엉덩이 길이'),
    ('FA-04', (605, 1440), 200, 'GREY SNEAKERS', '스웨이드 · 메시', '낮은 운동화'),
]


def item_hex(pid, c, span):
    cx, cy = c
    q = span / 4
    return mean_hex(pid, (cx - q, cy - q, cx + q, cy + q))


# 장소 — 착장 사진의 배경에서 잰 자리(비율 x0, y0, x1, y1)
PLACES = [  # pid, 캡션 굵은 낱말, 캡션, 장소 자리, 아이템 번호(옷 색), 사진 가운데 · 폭
    ('FA-01', 'Riverside–', '밤 강변. 어두운 물빛 앞에 올리브 파카.', (0.0, 0.68, 0.35, 0.80), 0, (870, 1250), 1250),
    ('FA-04', 'Shop front–', '따뜻한 불빛의 가게 앞. 검정 롱코트.', (0.18, 0.30, 0.34, 0.60), 1, (640, 1000), 820),
    ('FA-05', 'Park–', '오후의 놀이공원. 밝은 베이지 재킷.', (0.25, 0.82, 0.60, 0.97), 4, (790, 1060), 760),
    ('FA-03', 'Seaside rocks–', '회색 바위와 바다. 회색 니트.', (0.0, 0.55, 0.35, 0.95), 2, (600, 700), 720),
]


def sw(x, y, hx, w=2.6, h=2.6):
    """색 견본 — 글과 따로 한 상자 (InDesign 에서 글 사이 틈이 사라지지 않게)."""
    return d(x, y, w, h, '', 'swb', f"data-hex='{hx}'").replace("style='", f"style='background:{hx};", 1)


def cmf(x, y, w, rows):
    """사례 6 Desjobert CMF 줄: 가는 선 · 굵은 영문 머리 · 값 (COLOR 는 견본 + HEX)."""
    o = []
    for r, (k, v, hx) in enumerate(rows):
        yy = y + r * 3.9
        o.append(d(x, yy, w, .15, '', 'rl'))
        o.append(d(x, yy + .55, 15, 3.4, f'<p>{k}</p>', 't cmk'))
        if hx:
            o.append(sw(x + 15, yy + .9, hx))
            o.append(d(x + 18.6, yy + .55, w - 18.6, 3.4, f'<p>{v}</p>', 't cmv'))
        else:
            o.append(d(x + 15, yy + .55, w - 15, 3.4, f'<p>{v}</p>', 't cmv'))
    return ''.join(o)


# ── 공통 ─────────────────────────────────────────────────────────────────────────────
def rules(col=INK, a=.45):
    ln = lambda x1, y1, x2, y2, wd, aa: (f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' "
                                         f"style='stroke:{col};stroke-opacity:{aa};stroke-width:{wd}'/>")
    g = ln(L, TOP, R, TOP, .3175, a) + ln(L, BOT, R, BOT, .3175, a)
    for x in (L, CX, R):
        for y in (TOP, BOT):
            g += ln(x - 1.8, y, x + 1.8, y, .2, .9) + ln(x, y - 1.8, x, y + 1.8, .2, .9)
    return f"<svg class='ov' viewBox='0 0 {W} {H}'>{g}</svg>"


def folio(n, name):
    return (d(L, FOLIO_Y, 160, 4, '<p>FROM THE INSIDE&nbsp;&nbsp;—&nbsp;&nbsp;PART 2 MATCH</p>', 't ft')
            + d(107.5, FOLIO_Y, 100, 4, f'<p>{name}</p>', 't ft c')
            + d(261, FOLIO_Y, 40, 4, f'<p>{n:02d}</p>', 't ft r'))


def room(wall_x=WALL_X):
    """표지의 방: 파란 벽(왼쪽) · 흰 벽 · 살구색 바닥 + 사선."""
    return (f"<svg class='ov' viewBox='0 0 {W} {H}'><rect x='0' y='0' width='{W}' height='{H}' fill='{WHITE}'/>"
            f"<polygon points='0,{FLOOR_Y} {W},{FLOOR_Y} {W},{H} {DIAG_X},{H}' fill='{PEACH}'/>"
            f"<polygon points='0,0 {wall_x},0 {wall_x},{FLOOR_Y} {DIAG_X},{H} 0,{H}' fill='{BLUE}'/></svg>")


def label(pts, x_txt, w_txt):
    """사례 6 Desjobert 의 지시선: 점 → 꺾인 선 → 굵은 영문 + 한글."""
    svg, o = '', []
    for (px, py), ly, en, ko in pts:
        svg += (f"<circle cx='{px:.2f}' cy='{py:.2f}' r='.75' fill='{INK}'/>"
                f"<polyline points='{px:.2f},{py:.2f} {x_txt - 4:.2f},{ly:.2f} {x_txt - 1:.2f},{ly:.2f}' class='ld'/>")
        o.append(d(x_txt, ly - 2.2, w_txt, 8, f"<p class='e'>{en}</p><p>{ko}</p>", 't lb'))
    return svg, ''.join(o)


# ── 8 · 표지 (사용자 이미지 자리 표시 위 글) ───────────────────────────────────────────
def p08():
    return cm.guides() + cm.text()


# ── 9 · Front, or back? — 한 벌 안에서 맞춘다 ────────────────────────────────────────────
def p09():
    FL = FLOOR_Y + 3  # 사진 바닥(사람이 바닥선보다 조금 앞에 선다 — 표지의 인물처럼)
    front, f2mm = crop('FA-04', 112, FL - 122, 50, 122, 640, 900, 500)
    back, b2mm = crop('FA-03', 218, FL - 74, 58, 74, 640, 760, 640)
    s1, l1 = label([(f2mm(610, 540), 40, 'HAIR', '짧고 단정하게'), (f2mm(640, 930), 70, 'COAT', '검정 오버핏 롱코트'),
                    (f2mm(640, 1370), 112, 'TROUSERS', '네이비 와이드 팬츠'), (f2mm(600, 1455), 136, 'SHOES', '회색 스니커즈')], 168, 44)
    s2, l2 = label([(b2mm(650, 520), 92, 'SHOULDER', '어깨에서 떨어지는 품'), (b2mm(700, 760), 106, 'KNIT', '굵은 결')], 282, 24)
    X = L
    o = [room(),
         d(X, 14, 88, 4, '<p>PART 2&nbsp;&nbsp;—&nbsp;&nbsp;한 벌 안에서</p>', 't sm'),
         d(X, 19, 92, 30, '<p>FRONT,</p><p>OR BACK?</p>', 't ttl2'),
         d(X, 54, 86, 12, '<p>먼저 한 벌 안에서 맞춘다.</p><p>색과 원단, 길이를 머리부터 신발까지.</p>', 't ko9'),
         d(X, 72, 86, 18, '<p>매장 안의 손님은</p><p>마네킹의 등을 먼저 본다.</p>', 't ko15'),
         d(X, 94, 86, 14, '<p>그래서 앞만이 아니라 등까지 맞춘다 —</p><p>니트의 결, 어깨에서 떨어지는 품.</p>', 't ko8'),
         d(X, 112, 86, 22, '<p>INSIDE THE STORE,</p><p>PEOPLE MEET THE</p><p>MANNEQUIN’S BACK FIRST —</p><p>SO I MATCH THE BACK, TOO.</p>', 't sub'),
         front, back,
         f"<svg class='ov' viewBox='0 0 {W} {H}'>{s1}{s2}</svg>", l1, l2,
         d(112, FL + 2.5, 50, 4, '<p>(A)&nbsp;&nbsp;FRONT&nbsp;&nbsp;·&nbsp;&nbsp;N°FA-04</p>', 't sm s'),
         d(218, FL + 2.5, 58, 4, '<p>(B)&nbsp;&nbsp;BACK&nbsp;&nbsp;·&nbsp;&nbsp;N°FA-03</p>', 't sm s'),
         rules(), folio(9, 'FRONT, OR BACK?')]
    return ''.join(o)


# ── 10 · Selection—06. — 아이템끼리 맞춘다 ──────────────────────────────────────────────
def p10():
    NY0, SHELF = 44, 112               # 파란 진열 벽 y 44–112, 선반(바닥선) y 112
    n = len(ITEMS)
    gap = 5
    cw = (R - L - gap * (n - 1)) / n   # 43.7
    ch = 52
    o = [f"<svg class='ov' viewBox='0 0 {W} {H}'><rect x='0' y='0' width='{W}' height='{H}' fill='{WHITE}'/>"
         f"<rect x='0' y='{NY0}' width='{W}' height='{SHELF - NY0}' fill='{BLUE}'/>"
         f"<rect x='0' y='{SHELF}' width='{W}' height='{H - SHELF}' fill='{PEACH}'/></svg>",
         d(L, 14, 150, 4, '<p>PART 2&nbsp;&nbsp;—&nbsp;&nbsp;아이템끼리</p>', 't sm'),
         d(L, 18.5, 150, 22, '<p>SELECTION—06.</p>', 't ttl3'),
         d(172, 15, 129, 12, '<p>다음은 아이템끼리 맞춘다.</p><p>자주 입는 여섯을 재 보니, 네 가지 색 안에 있었다.</p>', 't ko9')]
    swatch = ''
    for i, (pid, c, span, en, mat, fit) in enumerate(ITEMS):
        x = L + i * (cw + gap)
        hx = item_hex(pid, c, span)
        html, _ = crop(pid, x, SHELF - ch - 3, cw, ch, c[0], c[1], span)
        o += [d(x, NY0 + 3, cw, 4, f'<p>({i + 1:02d})&nbsp;&nbsp;{en}</p>', 't sm w s'),
              html,
              d(x + 1.4, SHELF - ch - 1.6, 16, 4, f'<p>N°{pid}</p>', 't src'),
              cmf(x, SHELF + 4, cw, [('COLOR', hx, hx), ('MATERIAL', mat, None), ('FIT', fit, None)])]
        swatch += sw(172 + i * 6.8, 36, hx, 6, 3)
    o += [d(172, 30, 129, 4, '<p>06 ITEMS&nbsp;&nbsp;·&nbsp;&nbsp;4 COLOURS — BLACK · OLIVE · BEIGE · GREY&nbsp;&nbsp;·&nbsp;&nbsp;0 PRIMARY</p>', 't sm s'),
          swatch,
          d(L, 150, 150, 10, '<p>색을 줄이면, 무엇과 입어도 서로 맞는다.</p>', 't ko15'),
          d(172, 150, 129, 10, '<p>SIX THINGS I WEAR OFTEN, MEASURED:</p><p>FOUR COLOURS, NO PRIMARIES.</p>', 't sub'),
          d(L, 162, 150, 8, '<p>COLOR — 착장 사진(N°FA-01–05)의 그 자리 픽셀 평균 · MATERIAL · FIT — 사진에 보이는 것만</p>', 't note'),
          rules(), folio(10, 'SELECTION—06')]
    return ''.join(o)


# ── 11 · Four places, | four outfits. — 장소에 맞춘다 ──────────────────────────────────
def p11():
    RY0, RFL, RY1 = 44, 106, 122       # 방: 벽 y 44–106 (장소 색) · 바닥 106–122 (옷 색)
    gap = 4
    cw = (R - L - gap * 3) / 4         # 68.75
    o = [f"<svg class='ov' viewBox='0 0 {W} {H}'><rect x='0' y='0' width='{W}' height='{H}' fill='{WHITE}'/></svg>",
         d(L, 14, 138, 4, '<p>PART 2&nbsp;&nbsp;—&nbsp;&nbsp;장소에</p>', 't sm'),
         d(CX - 145.5, 18.5, 139.5, 16, '<p>FOUR PLACES,</p>', 't ttl4 r'),
         d(CX + 6, 18.5, 139.5, 16, '<p>FOUR OUTFITS.</p>', 't ttl4'),
         d(CX + 6, 33, 139, 10, '<p>마지막으로 장소에 맞춘다. 헤어와 옷의 톤을 그날 갈 장소에 맞춘다.</p>', 't ko8')]
    svg = ''
    for i, (pid, b, cap, pbox, it, (cx, cy), span) in enumerate(PLACES):
        x = L + i * (cw + gap)
        ph_hex = mean_hex(pid, pbox)
        ip = ITEMS[it]
        cl_hex = item_hex(ip[0], ip[1], ip[2])
        svg += (f"<rect x='{x:.2f}' y='{RY0}' width='{cw:.2f}' height='{RFL - RY0}' fill='{ph_hex}'/>"
                f"<polygon points='{x:.2f},{RFL} {x + cw:.2f},{RFL} {x + cw:.2f},{RY1} {x + 7:.2f},{RY1}' fill='{cl_hex}'/>"
                f"<polygon points='{x:.2f},{RFL} {x + 7:.2f},{RY1} {x:.2f},{RY1}' fill='{ph_hex}'/>")
        pw, phh = 34, 52
        html, _ = crop(pid, x + cw / 2 - pw / 2 + 4, RFL + 4 - phh, pw, phh, cx, cy, span)
        o += [html,
              d(x + 2.4, RY0 + 2.2, 30, 4, f'<p>N°0{i + 1}</p>', 't sm w s'),
              d(x, RY1 + 3, cw, 10, f'<p><b>{b}</b> {cap}</p>', 't cap wrap'),
              sw(x, RY1 + 13, ph_hex), d(x + 3.6, RY1 + 12.5, 24, 4, f'<p>{ph_hex}&nbsp;&nbsp;PLACE&nbsp;&nbsp;↔</p>', 't pair'),
              sw(x + 27.5, RY1 + 13, cl_hex), d(x + 31.1, RY1 + 12.5, cw - 31.1, 4, f"<p>{cl_hex}&nbsp;&nbsp;{ip[3].split(' ·')[0]}</p>", 't pair')]
    o.insert(1, f"<svg class='ov' viewBox='0 0 {W} {H}'>{svg}</svg>")
    o += [d(L, 145, 180, 12, '<p>옷은 놓인 장소와 맞을 때 완성된다.</p>', 't ko22'),
          d(L, 158.5, 150, 10, '<p>CLOTHES ARE COMPLETE ONLY</p><p>WHEN THEY MATCH THE PLACE.</p>', 't sub'),
          d(205, 147, 96, 14, '<p>라운딩 VMD 는 브랜드의 기준을 매장마다 맞추는 사람이다.</p><p>그러려면 먼저 공간을 알아야 한다.</p>', 't ko7'),
          d(205, 162, 96, 10, '<p>A ROUNDING VMD MATCHES THE BRAND TO EVERY STORE — SO FIRST, THE SPACE.</p>', 't sub xs wrap'),
          rules(), folio(11, 'FOUR PLACES, FOUR OUTFITS')]
    return ''.join(o)


PAGES = [(8, p08), (9, p09), (10, p10), (11, p11)]

KO = "'WenQuanYi Zen Hei',sans-serif"
CSS = cm.CSS + f"""
@font-face{{font-family:Mono;src:url('file://{FONTS}/IBMPlexMono-Regular.ttf')}}
.ov{{left:0;top:0;width:{W}mm;height:{H}mm}}.ph{{overflow:hidden}}.wrap p{{white-space:normal}}
.ft{{font-family:Mono,monospace;font-size:7pt;letter-spacing:.1em;color:{INK};white-space:nowrap}}.ft.c{{text-align:center}}.ft.r{{text-align:right}}
.sm.s{{font-size:6.6pt;line-height:8pt}}.sm.w{{color:{WHITE}}}
.ttl2{{font-family:Inst,sans-serif;font-weight:700;font-size:40pt;line-height:37pt;color:{WHITE};transform:scaleX(.74);transform-origin:0 0}}
.ttl3{{font-family:Inst,sans-serif;font-weight:700;font-size:46pt;line-height:46pt;color:{INK};transform:scaleX(.74);transform-origin:0 0}}
.ttl4{{font-family:Inst,sans-serif;font-weight:700;font-size:30pt;line-height:32pt;color:{INK};transform:scaleX(.74);transform-origin:0 0}}
.ttl4.r{{text-align:right;transform-origin:100% 0}}
.ko7,.ko8,.ko9,.ko15,.ko22{{font-family:{KO};color:{INK};word-break:keep-all}}
.ko7{{font-size:7.4pt;line-height:11pt}}.ko8{{font-size:8.2pt;line-height:12.4pt}}.ko9{{font-size:9.4pt;line-height:14pt}}
.ko15{{font-size:15pt;line-height:21pt;-webkit-text-stroke:.25pt {INK}}}
.ko22{{font-size:22pt;line-height:28pt;-webkit-text-stroke:.35pt {INK}}}
.sub.xs{{font-size:6.6pt;line-height:10.4pt}}
.lb{{font-family:{KO};font-size:6.8pt;line-height:9pt;color:{INK}}}.lb .e{{font-family:Inst,sans-serif;font-weight:700;letter-spacing:.09em;font-size:6.6pt}}
.ov .ld{{fill:none;stroke:{INK};stroke-width:.2}}
.src{{font-family:Mono,monospace;font-size:5.6pt;line-height:7pt;color:{INK};background:{WHITE};padding:0 .8mm;width:auto!important;height:auto!important}}
.cmk{{font-family:Inst,sans-serif;font-weight:700;font-size:6pt;line-height:9pt;letter-spacing:.09em;color:{INK}}}
.cmv{{font-family:{KO};font-size:6.8pt;line-height:9pt;color:{INK};white-space:nowrap}}
.rl{{background:rgba(27,27,26,.35)}}
.sw{{display:inline-block;width:2.6mm;height:2.6mm;vertical-align:-.45mm;margin-right:1.2mm}}
.note{{font-family:{KO};font-size:6.4pt;line-height:9pt;color:rgba(27,27,26,.7)}}
.cap{{font-family:{KO};font-size:7.2pt;line-height:10.6pt;color:{INK};word-break:keep-all}}.cap b{{font-family:Inst,sans-serif;font-weight:700}}
.pair{{font-family:Mono,monospace;font-size:5.8pt;letter-spacing:.04em;color:{INK};white-space:nowrap}}
"""


def html_doc(pages=PAGES):
    sheets = ''.join(f"<div class='sheet' style='background:{WHITE}'>{fn()}</div>" for _, fn in pages)
    return (f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU part 2 Match</title><style>{CSS}</style></head>"
            f"<body>{sheets}</body></html>")


def main():
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'part2_match.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(html_doc())
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'part2_match.pdf'), os.path.join(TMP, 'part2')], check=True)


if __name__ == '__main__':
    main()
