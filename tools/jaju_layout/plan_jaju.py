"""JAJU 포트폴리오 — '자주 스타일' 안: 기존 안(B10)의 쪽 순서 그대로, 자주 홈페이지 기획전 · 기사의 문법으로 바꾼 판.

  python3 tools/jaju_layout/plan_jaju.py   ->  docs/jaju_rounding_vmd/layout/plan_jaju.pdf

사용자: "B10 은 기존 안으로 유지한다. 자주 홈페이지의 이미지 및 기사이다. '기존 안'을 자주가 추구하는 스타일에 맞도록 변형.
페이지의 순서는 유지한다. 각 페이지 내에서 이미지의 레이아웃, 색상, 텍스트는 임의 판단하에 변경을 허락한다."
분석 · 쪽별 대응: docs/jaju_rounding_vmd/plan_jaju.md

자주 기획전(자주하니까 · JUST PROJECT · 2026 가을/겨울 캠페인)에서 가져온 문법
  첫 화면     왼쪽 밝은 판(작은 표지 글 · 두 줄 제목, 한 낱말만 색 · 가는 세로선 · 두 줄 설명) | 오른쪽 사진
  색 띠       첫 화면 아래 쪽 폭 전체의 색 띠, 가운데 굵은 한 줄 + 두 줄
  인터뷰 머리 [ JAJU INTERVIEW ] 꼬리표 → 이름(색) + 제목 → 한 줄 설명, 모두 가운데
  사진        흰 테 + 옅은 그림자, 크기가 다른 사진을 엇갈려 겹침 (JUST PROJECT 는 살짝 기울인 카드 + 리본 꼬리표)
  목록        색 꼬리표(ITEM · APPAREL) 아래 ✓ 목록, 사진 속 물건에 ⊕ 표시
  상품 줄     회색 칸에 물건, 아래 이름 두 줄
  바탕 · 색   따뜻한 미색 종이, 기획전마다 한 색 — 장 1 청록 · 장 2 겨자 · 장 3 장미
가져오지 않은 것: 자주 로고 · 사진(W2-D25), 손 그림 낙서(새 이미지 — 필요하면 Codex, CLAUDE.md), 종이 질감(새 이미지).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b10 as b10  # noqa: E402  (보정 · 잘라 쓰기 패치가 모두 걸린 상태)

b4, b3, pe = b10.b4, b10.b3, b10.pe
pc, t, div, photo, e, af, frame = pe.pc, pe.t, pe.div, pe.photo, pe.e, pe.af, pe.frame
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT
NAME = pe.NAME
crop, mean_hex = b4.crop, b4.mean_hex

PAPER, WHITE, INK, SUB, LINE = '#F6F2EC', '#FFFDFA', '#2B2622', '#7A716A', '#DDD4CA'
ACC = {  # 글자색, 띠 바탕, 띠 글자
    'rose': ('#C27E6E', '#EACFC6', '#3A2C27'),
    'teal': ('#3E7B85', '#3E7B85', '#F4F1EC'),
    'mustard': ('#B08A22', '#ECDFB5', '#3A3220'),
    'stone': ('#8C7B6B', '#E4DCD2', '#3A322B'),
}


# ── 부품 ────────────────────────────────────────────────────────────────────────────
def framed(pid, x, y, w, h, rot=0, **kw):
    """흰 테 + 그림자 사진."""
    st = f'transform:rotate({rot}deg);' if rot else ''
    return div(x - 1.6, y - 1.6, w + 3.2, h + 3.2, photo(pid, 1.6, 1.6, w, h, **kw), 'frm', st)


def framed_crop(pid, x, y, w, h, cx, cy, span, rot=0):
    st = f'transform:rotate({rot}deg);' if rot else ''
    return div(x - 1.6, y - 1.6, w + 3.2, h + 3.2, crop(pid, 1.6, 1.6, w, h, cx, cy, span), 'frm', st)


def label(x, y, w, s, cls='c'):
    return t(x, y, w, 5, f'[ {s} ]', 'lab ' + cls)


def heading(x, y, w, s, cls='c', size=''):
    return t(x, y, w, 12, s, f'hd {size} {cls}')


def desc(x, y, w, s, cls='c'):
    return t(x, y, w, 14, s, 'ds wrap ' + cls)


def chip(x, y, s):
    return t(x, y, None, 4.6, s, 'chip')


def checks(x, y, w, rows):
    return t(x, y, w, 60, ''.join(f"<div class='ck'><b>{a}</b><span>{b}</span></div>" for a, b in rows), 'cks')


def foot(n, part=''):
    return (t(14, 200, 160, 4, f"FROM THE INSIDE{('&nbsp;&nbsp;·&nbsp;&nbsp;' + part) if part else ''}", 'ft')
            + t(243, 200, 40, 4, f'{n:02d}', 'ft r'))


def head(y, lab, hd, ds, w=240):
    x = (297 - w) / 2
    return label(x, y, w, lab) + heading(x, y + 6, w, hd) + desc(x, y + 18, w, ds)


def hero(pid, focus, mark, title, sub, band_t, band_s, n=None, part='', vf=False, right=True, flip=False, zoom=1.0):
    """자주하니까 첫 화면: 밝은 판 | 사진, 아래 색 띠."""
    px, lx = (118, 0) if right else (0, 179)
    img = photo(pid, px, 0, 179, 160, focus=focus, zoom=zoom)
    if flip:
        img = img.replace('<img ', "<img class='flip' ", 1)
    o = [div(lx, 0, 118, 160, '', 'panel'), img,
         t(lx + 10, 40, 98, 5, mark, 'mark c'),
         t(lx + 6, 52, 106, 40, title, 'ht c'),
         div(lx + 58.8, 96, .2, 12, '', 'vline'),
         t(lx + 8, 114, 102, 20, sub, 'hs c wrap'),
         div(0, 160, 297, 50, '', 'band'),
         t(20, 172, 257, 7, band_t, 'bt c'),
         t(30, 181, 237, 14, band_s, 'bs c wrap')]
    if vf:
        o.append(viewfinder(px + 8, 8, px + 171, 152))
    if n is not None:
        o.append(t(14, 202, 160, 4, f"FROM THE INSIDE{('&nbsp;&nbsp;·&nbsp;&nbsp;' + part) if part else ''}", 'ft bf'))
        o.append(t(243, 202, 40, 4, f'{n:02d}', 'ft bf r'))
    return ''.join(o)


def viewfinder(x0, y0, x1, y1, r=6):
    def c(x, y, dx, dy):
        pts = f'{x + dx * r},{y} {x},{y} {x},{y + dy * r}'
        return f"<polyline points='{pts}' class='vfs'/><polyline points='{pts}' class='vf'/>"
    g = c(x0, y0, 1, 1) + c(x1, y0, -1, 1) + c(x0, y1, 1, -1) + c(x1, y1, -1, -1)
    return div(0, 0, 297, 210, f"<svg class='ov' viewBox='0 0 297 210'>{g}</svg>", '')


def plus(x, y):
    """자주 기획전의 ⊕ 표시 — 사진 속 물건."""
    return div(x - 2.2, y - 2.2, 4.4, 4.4, '+', 'plus')


# ── 표지 ──────────────────────────────────────────────────────────────────────────────
def p_cover():
    return hero('COVER', (0.72, 0.42), 'FROM THE INSIDE',
                '<p>안에서 보면</p><p><em>사람이 보인다</em></p>',
                f'<p>JAJU 라운딩 VMD 지원 포트폴리오</p><p><b>{NAME}</b></p>',
                'Visual Merchandiser Portfolio · 2026',
                '<p>밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.</p>'
                '<p class="en">From the street you see the products. From inside, you see the people.</p>')


# ── 01 · Prologue ─────────────────────────────────────────────────────────────────────
def p_prologue():
    body = ''.join(f'<p>{e(l)}</p>' for l in pc.LEAD_KO[:-1])
    parts = [('/01', 'Observe.', '관찰하다 — 사진', '02', 'teal'), ('/02', 'Contain.', '담다 — 건축', '06', 'mustard'),
             ('/03', 'Fill.', '채우다 — 패션', '09', 'rose')]
    o = [label(28, 18, 241, 'PROLOGUE'),
         heading(28, 25, 241, '밖에서 보면 상품이 보이고, <em>안에서 보면 사람이 보인다</em>'),
         t(48, 40, 201, 50, body, 'pro c'),
         t(48, 90, 201, 6, f'<p>{e(pc.LEAD_KO[-1])}</p>', 'prob c'),
         t(58, 100, 181, 20, pc.LEAD_EN, 'en c wrap'),
         div(0, 132, 297, 54, '', 'band')]
    for i, (n, w, k, p, a) in enumerate(parts):
        x = 24 + i * 85
        o.append(t(x, 141, 79, 36, f"<p class='pn' style='color:{ACC[a][0]}'>{n}</p><p class='pw'>{w}</p><p class='pk'>{k}&nbsp;&nbsp;·&nbsp;&nbsp;p.{p}</p>", 'part c'))
    o.append(div(108.5, 144, .2, 26, '', 'vline'))
    o.append(div(193.5, 144, .2, 26, '', 'vline'))
    o.append(foot(1))
    return ''.join(o)


# ── 02 · /01 Observe ─────────────────────────────────────────────────────────────────
def p_observe():
    return hero('PH-13', (0.5, 0.4), '/01&nbsp;&nbsp;OBSERVE',
                '<p>가게 밖, 스쳐 지나가는</p><p>일상에서도 나는</p><p><em>사람들을 눈여겨본다.</em></p>',
                '<p class="en">Outside the shop, in everyday moments, I keep watching people.</p>',
                'PART 1 · 관찰하다', '<p>사진 17장 — 사람들이 걸음을 늦추고 멈춘 자리를 기록했다.</p>',
                n=2, part='PART 1 OBSERVE', vf=True)


# ── 03 · Where people stop — 인터뷰 머리 + 흰 테 콜라주 ───────────────────────────────────
def p_grid():
    o = [head(12, 'OBSERVE NOTE', '사람들이 <em>멈춘 자리</em>',
              '눈여겨보면 보인다. 사람들은 무언가 앞에서 걸음을 늦추고, 같은 곳을 함께 바라본다.')]
    cells = [  # pid, x, y, w, h, focus, rot, 이름, 행동
        ('PH-11', 18, 56, 64, 42, (0.6, 0.5), 0, 'Alley', '누군가는 지나가고, 누군가는 계단에 앉아 쉰다.'),
        ('PH-06', 96, 46, 104, 64, (0.35, 0.5), 0, 'Food truck', '주문하기 전, 메뉴판 사진 앞에서 먼저 멈춘다.'),
        ('PH-04', 214, 52, 66, 44, (0.6, 0.55), 0, 'Snack stand', '여럿이 같은 메뉴판을 함께 올려다본다.'),
        ('PH-17', 30, 122, 60, 40, (0.55, 0.55), 0, 'Breakwater', '접힌 파라솔 아래, 한 사람이 바다를 보고 앉았다.'),
        ('PH-01', 112, 130, 70, 42, (0.6, 0.6), 0, 'Beach', '사람들은 물이 얕은 곳에 모여 선다.'),
        ('PH-03', 200, 116, 80, 46, (0.3, 0.55), 0, 'Canoe', '해가 지는 쪽으로, 같은 박자로 노를 젓는다.'),
    ]
    for pid, x, y, w, h, f, r, nm, act in cells:
        o.append(framed(pid, x, y, w, h, r, focus=f))
        o.append(t(x, y + h + 3, w + 4, 10, f'<p><b>{nm}</b>&nbsp;&nbsp;{act}</p>', 'cap wrap'))
    o += [chip(200, 180, 'NOTE'), t(214, 180.2, 80, 5, '사람이 멈춘 자리는 진열이 놓일 자리다.', 'notek'),
          foot(3, 'PART 1 OBSERVE')]
    return ''.join(o)


# ── 04 · What made me stop — 큰 사진 + 꼬리표 목록 ─────────────────────────────────────
def p_detail():
    W, H = 152, 86

    def chair(to, s):
        cx, cy = to(1072, 578)
        return af(cx, cy, 6.5, f'a)  {pe.accent("PH-05")}', 'left') + frame(6, 6, W - 12, H - 24, 'WIDE')

    def pink(to, s):
        return af(*to(687, 545), 4, 'b)')

    def sig(to, s):
        return af(*to(880, 94), 3.4, 'c)')

    def rail(to, s):
        x0, y0 = to(300, 60)
        return frame(x0, y0, 400 * s, 640 * s, 'd)') + af(*to(707, 600), 2.6)

    return ''.join([
        framed('PH-05', 18, 22, W, H, marks=chair),
        framed('PH-01', 18, 124, 46, 42, -1.5, focus=(0.458, 0.64), zoom=3.0, marks=pink),
        framed('PH-08', 71, 130, 46, 42, 1, focus=(0.6, 0.2), zoom=1.6, marks=sig),
        framed('PH-07', 124, 122, 46, 42, -.8, focus=(0.33, 0.45), marks=rail),
        label(188, 26, 96, 'OBSERVE NOTE', 'l'),
        heading(188, 33, 96, '눈이 <em>먼저</em> 가는 한 점', 'l'),
        desc(188, 46, 92, '넓은 장면에서도 눈은 한 점에 먼저 간다.', 'l'),
        chip(188, 62, 'POINT'),
        checks(188, 70, 96, [('a) Red chair', '파란 바다, 모서리의 빨강'), ('b) Pink', '수십 명 가운데 한 사람'),
                             ('c) Signal', '어둠 속 빨간 신호'), ('d) Through the rail', '난간 너머, 불 앞에 선 사람의 등')]),
        t(188, 140, 96, 30, '<p>진열도 같다.</p><p>시선이 먼저 닿을 한 점을 정하고,</p><p>그 점이 놓일 자리를 만든다.</p>', 'say'),
        foot(4, 'PART 1 OBSERVE'),
    ])


# ── 05 · Reading a window ───────────────────────────────────────────────────────────
def p_reading():
    def shop(to, s):
        ey = to(0, 620)[1]
        return (f"<line x1='0' y1='{ey:.1f}' x2='60' y2='{ey:.1f}' class='afl'/><text x='1.5' y='{ey - 1.2:.1f}' class='afs'>a) EYE LEVEL</text>"
                + af(*to(815, 700), 3.2, 'b)') + af(*to(925, 705), 3.2, 'c)') + af(*to(790, 560), 2.8, 'd)', 'left') + af(*to(905, 410), 2.6, 'e)'))

    def truck(to, s):
        return (frame(*to(808, 200), 210 * s, 350 * s, 'f) TOP') + frame(*to(1215, 140), 280 * s, 490 * s, 'g) SIDE')
                + frame(*to(567, 560), 400 * s, 280 * s, 'h) LOW') + af(*to(683, 318), 3.2, 'i)'))

    return ''.join([
        head(12, 'OBSERVE NOTE', '남의 진열창도 <em>같은 눈</em>으로 읽는다', '눈이 먼저 가는 곳, 손이 닿는 곳.'),
        framed('FA-04', 22, 46, 60, 140, focus=(888 / 1202, 610 / 1500), zoom=2.6, marks=shop),
        chip(92, 52, 'WINDOW'),
        checks(92, 60, 60, [('a) Eye level', '눈높이'), ('b) Hero', '가장 진한 색의 병'), ('c) Repeat', '같은 잔의 줄'),
                            ('d) Green', '초록 하나'), ('e) Light', '위에서 떨어지는 빛')]),
        t(92, 172, 60, 10, '<p>FA-04 · 생활용품 가게 진열창</p><p>PH-06 · 푸드 트럭 메뉴판</p>', 'data'),
        framed('PH-06', 162, 46, 116, 66, focus=(0.6, 0.45), marks=truck),
        chip(162, 122, 'MENU BOARD'),
        checks(162, 130, 116, [('f) Top', '멀리서 먼저 보이는 칸'), ('g) Side', '멈춘 뒤에 읽는 칸'),
                               ('h) Low', '손에 닿는 높이'), ('i) Inside', '창 안의 사람')]),
        t(162, 172, 116, 12, '라운딩 VMD 는 매장을 돌며 같은 질문을 한다 — 눈높이에 무엇이 있는가, 멈춘 뒤에 무엇을 읽는가.', 'ds wrap l'),
        foot(5, 'PART 1 OBSERVE'),
    ])


# ── 06 · /02 Contain ─────────────────────────────────────────────────────────────────
def p_contain():
    return hero('AR-03', (0.55, 0.5), '/02&nbsp;&nbsp;CONTAIN',
                '<p>멈춘 자리에는</p><p><em>늘 틀이 있었다.</em></p>',
                '<p>무엇을 채우고 무엇을 비울지가</p><p>그 안의 하루를 정한다.</p>',
                'PART 2 · 담다', "<p>'담' 안의 ㅁ 은 한옥의 마당이자 진열대의 한 칸이다. — 건축학과 작업 10점</p>",
                n=6, part='PART 2 CONTAIN', vf=True)


# ── 07 · From the city to the room ─────────────────────────────────────────────────
def p_collage():
    def red(to, s):
        return af(*to(1525, 715), 4)

    def yard(to, s):
        x0, y0 = to(380, 140)
        return frame(x0, y0, 330 * s, 400 * s)

    def cap(x, y, w, ttl, txt, pid):
        return t(x, y, w, 9, f'<p><b>{ttl}</b>&nbsp;&nbsp;{txt}&nbsp;&nbsp;<span class="pid">{pid}</span></p>', 'cap')

    return ''.join([
        head(12, 'CONTAIN NOTE', '도시에서 <em>방</em>으로', '도시에서 마당으로, 마당에서 길과 집으로. 틀을 좁혀 갈수록 그 안의 하루가 보인다.'),
        framed('AR-09', 18, 48, 116, 60, marks=red), cap(18, 111, 116, 'City', '도시의 광장 — 렌더', 'AR-09'),
        framed('AR-06', 34, 128, 62, 44, -1, focus=(0.5, 0.45), marks=yard), cap(34, 175, 70, 'Courtyard', '건물 사이를 비운 마당', 'AR-06'),
        framed('AR-05', 150, 46, 128, 54, focus=(0.45, 0.5)), cap(150, 103, 128, 'Path', '두 매스를 잇는 회랑과 길', 'AR-05'),
        framed('AR-10', 146, 118, 58, 56, 1), cap(146, 177, 60, 'House', '골목 언덕의 집', 'AR-10'),
        framed('AR-02', 218, 116, 60, 56, focus=(0.6, 0.45)), cap(218, 175, 62, 'Hollow', '도시 아래를 비운 단면', 'AR-02'),
        t(150, 188, 130, 5, '모형 · 렌더 — 건축학과 작업. 프로젝트 이름 · 학년 ____', 'data'),
        foot(7, 'PART 2 CONTAIN'),
    ])


# ── 08 · A room ─────────────────────────────────────────────────────────────────────
def p_room():
    def living(to, s):
        ey = to(0, 455)[1]
        lx, ly = to(548, 405)
        tx, ty = to(470, 480)
        return (f"<line x1='0' y1='{ey:.1f}' x2='168' y2='{ey:.1f}' class='afl'/><text x='2' y='{ey - 1.4:.1f}' class='afs'>a)  EYE LEVEL</text>"
                + af(lx, ly, 4, 'd)') + frame(tx, ty, 165 * s, 70 * s, 'c)'))

    def hood(to, s):
        return af(*to(627, 222), 4.5, 'b)')

    return ''.join([
        framed('AR-07', 18, 20, 168, 126, focus=(0.55, 0.55), marks=living),
        framed('AR-08', 118, 128, 84, 54, 1.5, focus=(0.55, 0.4), marks=hood),
        label(206, 26, 80, 'CONTAIN NOTE', 'l'),
        heading(206, 33, 80, '방 안에도 <em>진열</em>이 있다', 'l'),
        desc(206, 46, 78, '눈높이에 무엇을 두고, 어디에 빛을 주고, 무엇을 한 자리에 모을지.', 'l'),
        chip(206, 66, 'ROOM'),
        checks(206, 74, 80, [('a) Eye level', '눈이 머무는 높이'), ('b) Red point', '빨간 후드 — 시선이 먼저 닿는 곳'),
                             ('c) Set', '식탁 · 의자 · 책 — 한 자리의 조합'), ('d) Light', '스탠드 하나의 빛')]),
        t(206, 176, 80, 8, '<p>AR-07 거실 · 식당 모형</p><p>AR-08 주방 모형</p>', 'data'),
        foot(8, 'PART 2 CONTAIN'),
    ])


# ── 09 · /03 Fill ───────────────────────────────────────────────────────────────────
def p_fill():
    return hero('FA-02', (0.45, 0.45), '/03&nbsp;&nbsp;FILL',
                '<p>웃음이 머문 곳에는</p><p><em>늘 조합이 있었다.</em></p>',
                '<p class="en">Where a smile stayed, there was always a combination.</p>',
                'PART 3 · 채우다', '<p>자주 입는 옷으로, 그날 갈 장소에 맞는 조합을 만든다.</p>',
                n=9, part='PART 3 FILL', vf=True)


# ── 10 · Four places ───────────────────────────────────────────────────────────────
def p_four():
    three = [('FA-04', (0.53, 0.55), '02', 'EVENING', '가게 앞', 104, 52, 1), ('FA-05', (0.72, 0.6), '03', 'AFTERNOON', '공원', 162, 46, -1),
             ('FA-03', (0.6, 0.5), '04', 'SUNNY', '바닷가 바위', 220, 54, .8)]
    o = [head(12, 'STYLING NOTE', '네 장소, <em>네 벌</em>', '나는 그날 갈 장소에 옷의 톤을 맞춘다. 장소가 틀이라면, 옷은 그 틀을 채우는 조합이다.'),
         framed('FA-01', 22, 48, 66, 118, focus=(0.55, 0.6)),
         t(22, 170, 70, 5, 'N°01&nbsp;&nbsp;NIGHT · 강변', 'data')]
    for pid, f, n, tod, place, x, y, r in three:
        o.append(framed(pid, x, y, 50, 68, r, focus=f))
        o.append(t(x, y + 72, 54, 5, f'N°{n}&nbsp;&nbsp;{tod} · {place}', 'data'))
    sw = ''.join(f"<div><i style='background:{h}'></i><b>{name}</b><span>{h}</span></div>"
                 for h, name in ((mean_hex(pid, box), name) for pid, box, name in b4.OUTFITS))
    o += [chip(104, 150, 'PALETTE'), t(124, 150.2, 120, 5, '착장 사진에서 잰 색', 'notek'),
          div(104, 158, 176, 22, sw, 'pal2'), foot(10, 'PART 3 FILL')]
    return ''.join(o)


# ── 11 · Items — 상품 줄 ────────────────────────────────────────────────────────────
def p_items():
    o = [head(12, 'ITEM', '자주 입는 <em>여섯 가지</em>', '조합은 아이템에서 시작한다. 자주 입는 여섯 가지를 진열하듯 하나씩 놓았다.')]
    w, h, gap, x0 = 40.5, 58, 3.4, 18.5
    for i, (pid, (cx, cy), span, en, ko) in enumerate(b4.ITEMS):
        x = x0 + i * (w + gap)
        half = span / 2
        hx = mean_hex(pid, (int(cx - half / 2), int(cy - half / 2), int(cx + half / 2), int(cy + half / 2)))
        o.append(div(x, 52, w, h, '', 'card'))
        o.append(crop(pid, x + 3, 55, w - 6, h - 6, cx, cy, span))
        o.append(t(x, 114, w, 14, f"<p class='nk'>{ko}</p><p class='ne'>{en}</p><p class='nh'><i style='background:{hx}'></i>{hx}</p>", 'prod c'))
    o += [chip(18.5, 150, 'NOTE'), t(32, 150.2, 200, 5, '사진은 착장 사진(FA-01–05)에서 잘라 냈고, 색은 그 자리 픽셀의 평균이다.', 'notek'),
          foot(11, 'PART 3 FILL')]
    return ''.join(o)


# ── 12 · Breakdown — ⊕ 표시 + APPAREL 목록 ───────────────────────────────────────────
def p_breakdown():
    x0, y0, w, h = 26, 16, 96, 178
    W, H = 1202, 1500
    s = max(w / W, h / H)
    ox = min(0, max(w - W * s, w / 2 - 0.53 * W * s))
    oy = min(0, max(h - H * s, h / 2 - 0.5 * H * s))
    pts = [(610, 540), (640, 930), (640, 1370), (600, 1455)]
    return ''.join([
        framed('FA-04', x0, y0, w, h, focus=(0.53, 0.5)),
        ''.join(plus(x0 + ox + px * s, y0 + oy + py * s) for px, py in pts),
        label(140, 24, 140, 'STYLING NOTE', 'l'),
        heading(140, 31, 140, '손님은 <em>등</em>을 먼저 본다', 'l'),
        t(140, 44, 140, 6, 'Front, or back? Inside the store, people meet the mannequin’s back first.', 'en l'),
        desc(140, 53, 130, '매장 안의 손님은 마네킹의 등을 먼저 본다. 그래서 나는 등을 먼저 입힌다 — 니트의 결, 어깨에서 떨어지는 품.', 'l'),
        chip(140, 72, 'APPAREL'),
        checks(140, 80, 52, [('HAIR', '짧고 단정하게'), ('COAT', '검정 오버핏 롱코트'), ('TROUSERS', '네이비 와이드 팬츠'),
                             ('SHOES', '회색 스니커즈')]),
        framed('FA-03', 200, 86, 78, 82, 1.2, focus=(0.6, 0.5)),
        t(200, 172, 80, 5, 'FA-03 · 등과 니트의 결', 'data'),
        foot(12, 'PART 3 FILL'),
    ])


# ── 13 · Proposal — JUST PROJECT 의 STEP 카드 + 칸 ───────────────────────────────────
def p_proposal():
    steps = [('FA-04', (888, 610), 360, 'STEP 01. OBSERVE', '눈높이 가운데를 본다 — 05', 18, 50, -2),
             ('AR-07', (548, 420), 520, 'STEP 02. CONTAIN', '칸을 세우고 비울 칸을 남긴다 — 08', 84, 60, 1.5),
             ('FA-04', (640, 930), 520, 'STEP 03. FILL', '내 옷과 생활 물건으로 채운다 — 12', 40, 124, -1)]
    o = [head(12, 'PROPOSAL', '세 파트를 <em>한 칸</em>에 모은다', '생활의 물건 사이, 눈높이 가운데 칸에 옷의 조합 하나.')]
    for pid, (cx, cy), span, rib, txt, x, y, r in steps:
        o.append(div(x, y, 62, 58, crop(pid, 4, 4, 54, 36, cx, cy, span)
                     + t(4, 42.5, None, 5, rib, 'ribbon') + t(4, 50, 56, 5, txt, 'stx'), 'card2', f'transform:rotate({r}deg);'))
    x0, y0, cw, ch = 168, 48, 36, 38
    cells = [('AR-07', (548, 420), 220, 'Light'), None, ('FA-03', (650, 760), 360, 'Knit'),
             ('FA-02', (230, 610), 260, 'Shirt'), ('FA-04', (640, 950), 700, 'Outfit'), ('AR-07', (550, 520), 300, 'Table'),
             None, ('FA-04', (605, 1440), 200, 'Shoes'), None]
    for i, cell in enumerate(cells):
        r, c = divmod(i, 3)
        x, y = x0 + c * cw, y0 + r * ch
        o.append(div(x + 1.2, y + 1.2, cw - 2.4, ch - 2.4, '', 'cellbg' + ('' if cell else ' void')))
        if cell:
            pid, (cx, cy), span, w = cell
            o.append(crop(pid, x + 3.5, y + 3.5, cw - 7, ch - 11, cx, cy, span))
        o.append(t(x + 3.5, y + ch - 6.5, cw - 7, 4, cell[3] if cell else 'Void', 'cell2' + ('' if cell else ' void')))
    ey = y0 + ch * 1.45
    g = f"<line x1='{x0 - 8}' y1='{ey}' x2='{x0 + 3 * cw + 6}' y2='{ey}' class='hld2'/><text x='{x0 - 8}' y='{ey - 1.4}' class='hlt2'>EYE LEVEL</text>"
    o += [div(0, 0, 297, 210, f"<svg class='ov' viewBox='0 0 297 210'>{g}</svg>", ''),
          t(x0, y0 + 3 * ch + 3, 110, 5, 'ELEVATION — 한 칸의 진열 (제안 · 치수 없음)', 'data'),
          t(110, 184, 160, 8, '제안 — 실제로 시공하거나 진열한 것이 아니라 구상이다. 칸 속은 이 책에 실린 내 옷과 모형 속 물건이고, 치수는 매장을 재서 정한다.', 'ds wrap l'),
          foot(13)]
    return ''.join(o)


# ── 14 · Often — 캠페인 쪽 ──────────────────────────────────────────────────────────
def p_often():
    row = [('COVER', (0.76, 0.45), 'FROM THE INSIDE'), ('PH-04', (0.6, 0.5), 'OBSERVE'), ('AR-03', (0.6, 0.5), 'CONTAIN'),
           ('AR-07', (0.5, 0.55), 'A ROOM'), ('FA-02', (0.45, 0.45), 'FILL')]
    o = [t(28, 20, 241, 10, "자주 보고, 자주 담고, <em>자주</em> 채운다.", 'hd big c'),
         t(28, 33, 241, 5, 'O F T E N', 'spaced c'),
         t(48, 42, 201, 20, '<p>JAJU 는 “자주 쓸수록, 최상의 삶”이라고 말한다. 진열도 자주 볼수록 정확해진다.</p>'
                            '<p>나는 매장을 돌며 자주 보고, 그 자리에 맞게 담고, 손님의 하루에 맞는 조합으로 채우는 VMD 가 되려 한다.</p>', 'pro c wrap')]
    for i, (pid, f, w) in enumerate(row):
        x = 22 + i * 52.5
        o.append(framed(pid, x, 74, 46, 74, (-1, .8, -.5, 1, -.8)[i], focus=f))
        o.append(t(x, 152, 48, 5, f'N°{i + 1:02d}&nbsp;&nbsp;{w}', 'data c'))
    o += [t(48, 166, 201, 16, 'JAJU says, “the more often you use it, the better life becomes.” A display, too, becomes more precise the more often it is looked at. '
                             'I want to be a VMD who looks often, holds each place as it is, and fills it with what fits the day.', 'en c wrap'),
          foot(14)]
    return ''.join(o)


# ── 15 · About — 인터뷰 ─────────────────────────────────────────────────────────────
def p_about():
    rows = [('MAJOR', '건축학과 · 학교 · 학년 ____'), ('APPLYING', 'JAJU 라운딩 VMD'),
            ('EXPERIENCE', '판매 · 진열 · 매장 경험 ____'), ('ROUNDING', '출장 · 장기 근무 가능 여부 ____'),
            ('IN THIS BOOK', '사진 17 · 건축 작업 10 · 착장 5 — 모두 직접 찍고 만든 것'),
            ('CONTACT', '전화 ____ · 이메일 ____'), ('IMAGE CREDIT', '표지 이미지 ____ (직접 촬영 / 출처)')]
    tbl = ''.join(f"<div class='ab2'><b>{a}</b><span>{b}</span></div>" for a, b in rows)
    return ''.join([
        framed('FA-05', 26, 18, 96, 164, -1, focus=(0.74, 0.62), zoom=1.5),
        t(26, 186, 96, 5, 'FA-05 · 놀이공원 기념품 노점 앞', 'data'),
        label(140, 26, 140, 'ABOUT', 'l'),
        heading(140, 33, 140, '사람이 <em>멈추는 자리</em>를 보는 사람', 'l'),
        t(140, 46, 140, 6, f'I’m {NAME}.', 'en l'),
        desc(140, 55, 130, '사람이 멈추는 자리를 보고, 그 자리에 맞는 조합을 세우는 사람이 되려 한다.', 'l'),
        t(140, 72, 140, 100, tbl, 'abt2'),
        foot(15),
    ])


# ── 뒤표지 ───────────────────────────────────────────────────────────────────────────
def p_back():
    cr = ' &nbsp;·&nbsp; '.join([f'PHOTOGRAPHY — {NAME}', 'ARCHITECTURE MODELS — 과제명 · 연도 ____', f'STYLING — {NAME}', 'COVER IMAGE — ____'])
    return hero('COVER', (0.6, 0.42), 'FROM THE INSIDE',
                '<p>Thank you.</p><p><em>이제 당신은 밖에 있다.</em></p>',
                f'<p>CONTACT · {NAME}</p><p>전화 ____ · 이메일 ____</p>',
                '유리의 글자가 바로 읽힌다.', f'<p class="cr">{cr}</p>', right=False, flip=True)


PAGES = [(p_cover, 'rose', ''), (p_prologue, 'rose', ''), (p_observe, 'teal', 'g1'), (p_grid, 'teal', 'g1'), (p_detail, 'teal', 'g1'),
         (p_reading, 'teal', 'g1'), (p_contain, 'mustard', 'g1'), (p_collage, 'mustard', 'g1'), (p_room, 'mustard', 'g1'),
         (p_fill, 'rose', 'g1'), (p_four, 'rose', 'g1'), (p_items, 'rose', 'g1'), (p_breakdown, 'rose', 'g1'),
         (p_proposal, 'stone', 'g1'), (p_often, 'stone', 'g1'), (p_about, 'stone', 'g1'), (p_back, 'stone', '')]

KO = "'WenQuanYi Zen Hei',sans-serif"
CSS = pe.CSS + f"""
.sheet{{background:{PAPER}}}
.panel{{background:{PAPER}}}.band{{background:var(--band)}}.vline{{background:{INK};opacity:.35}}
.mark{{font-family:Mono,monospace;font-weight:700;font-size:8pt;letter-spacing:.14em;color:{INK};white-space:nowrap}}
.ht{{font-family:{KO};font-weight:700;font-size:19pt;line-height:28pt;color:{INK}}}.ht em,.hd em{{font-style:normal;color:var(--ac)}}
.hs{{font-family:{KO};font-size:8.4pt;line-height:13.5pt;color:{SUB}}}.hs b{{color:{INK}}}.hs p{{white-space:normal}}
.hs .en,.bs .en,.en{{font-family:Lora,serif;font-style:italic;font-size:8.4pt;line-height:12.5pt;color:{SUB}}}
.bt{{font-family:{KO};font-weight:700;font-size:11pt;color:var(--bandtx);white-space:nowrap}}
.bs{{font-family:{KO};font-size:8pt;line-height:13pt;color:var(--bandtx);opacity:.85}}.bs p{{white-space:normal}}.bs .en{{color:var(--bandtx)}}
.bs .cr{{font-family:Mono,monospace;font-size:5pt;letter-spacing:.06em}}
.lab{{font-family:{KO};font-weight:700;font-size:6.6pt;letter-spacing:.06em;color:{INK};white-space:nowrap}}
.hd{{font-family:{KO};font-weight:700;font-size:16pt;line-height:22pt;color:{INK};white-space:nowrap}}.hd.big{{font-size:20pt}}
.ds{{font-family:{KO};font-size:8.2pt;line-height:13pt;color:{SUB}}}.ds p{{white-space:normal}}.wrap{{word-break:keep-all}}
.frm{{background:{WHITE};box-shadow:0 .5mm 2.2mm rgba(70,50,30,.2)}}
.cap{{font-family:{KO};font-size:6.8pt;line-height:10pt;color:{SUB};word-break:keep-all}}.cap p{{white-space:normal}}
.cap b{{font-family:Lora,serif;font-weight:700;font-size:7.6pt;color:{INK}}}.cap .pid{{font-family:Mono,monospace;font-size:5pt;color:#A69C92}}
.chip{{font-family:Mono,monospace;font-weight:700;font-size:6.2pt;letter-spacing:.08em;color:#fff;background:var(--ac);padding:.6mm 2mm;white-space:nowrap;border-radius:.6mm}}
.notek{{font-family:{KO};font-weight:700;font-size:8pt;color:{INK};white-space:nowrap}}
.cks .ck{{position:static;display:flex;gap:2.4mm;align-items:baseline;padding:1.7mm 0;border-bottom:.15mm solid {LINE}}}
.cks .ck:before{{content:'✓';font-family:{KO};font-size:7.6pt;color:var(--ac)}}
.cks .ck b{{font-family:Lora,serif;font-weight:700;font-size:7.8pt;color:{INK};white-space:nowrap}}.cks .ck span{{font-family:{KO};font-size:7.4pt;color:{SUB}}}
.say{{font-family:{KO};font-weight:700;font-size:10pt;line-height:17pt;color:{INK}}}
.ft{{font-family:Mono,monospace;font-size:5.6pt;letter-spacing:.1em;color:#A69C92;white-space:nowrap}}.ft.bf{{color:var(--bandtx);opacity:.6}}
.data{{font-family:Mono,monospace;font-size:5.6pt;line-height:9pt;letter-spacing:.06em;color:{SUB};white-space:nowrap}}.data p{{white-space:nowrap}}
.pro{{font-family:{KO};font-size:8.6pt;line-height:15pt;color:{INK}}}.prob{{font-family:{KO};font-weight:700;font-size:9.2pt;color:{INK}}}
.part .pn{{font-family:Lora,serif;font-style:italic;font-size:10pt}}.part .pw{{font-family:Young,serif;font-size:17pt;line-height:22pt;color:var(--bandtx)}}
.part .pk{{font-family:{KO};font-size:7.4pt;color:var(--bandtx);opacity:.8}}
.plus{{border-radius:50%;background:rgba(255,253,250,.92);border:.3mm solid var(--ac);color:var(--ac);font-family:Mono,monospace;font-weight:700;font-size:8pt;line-height:3.8mm;text-align:center}}
.pal2{{display:flex;gap:4mm}}.pal2 div{{position:static;display:flex;flex-direction:column;gap:.8mm;width:40mm}}
.pal2 i{{display:block;width:40mm;height:9mm;border-radius:1mm}}.pal2 b{{font-family:Mono,monospace;font-size:5.6pt;letter-spacing:.06em;color:{INK};font-weight:400}}
.pal2 span{{font-family:Mono,monospace;font-size:5.4pt;color:{SUB}}}
.card{{background:#ECE8E2}}.prod .nk{{font-family:{KO};font-weight:700;font-size:7.8pt;color:{INK}}}
.prod .ne{{font-family:Mono,monospace;font-size:5.2pt;letter-spacing:.06em;color:{SUB};margin-top:.6mm}}
.prod .nh{{font-family:Mono,monospace;font-size:5.2pt;color:{SUB};margin-top:.6mm}}.prod .nh i{{display:inline-block;width:2.2mm;height:2.2mm;vertical-align:-.3mm;margin-right:1mm}}
.card2{{background:{WHITE};box-shadow:0 .5mm 2.2mm rgba(70,50,30,.22)}}
.ribbon{{font-family:Mono,monospace;font-weight:700;font-size:6.2pt;letter-spacing:.04em;color:#fff;background:#2F4A6B;padding:.5mm 1.6mm;white-space:nowrap}}
.stx{{font-family:{KO};font-size:6.4pt;color:{SUB};white-space:nowrap}}
.cellbg{{background:{WHITE};box-shadow:0 .3mm 1.2mm rgba(70,50,30,.12)}}.cellbg.void{{background:transparent;box-shadow:none;border:.2mm dashed {LINE}}}
.cell2{{font-family:Mono,monospace;font-size:5.4pt;color:{INK}}}.cell2.void{{color:#B3A99F}}
.ov .hld2{{stroke:var(--ac);stroke-width:.25;stroke-dasharray:1 .8}}.ov .hlt2{{font-family:Mono,monospace;font-size:2.2px;fill:var(--ac)}}
.spaced{{font-family:Mono,monospace;font-size:7pt;letter-spacing:.3em;color:var(--ac);white-space:nowrap}}
.abt2 .ab2{{position:static;display:flex;gap:4mm;padding:2.6mm 0;border-bottom:.15mm solid {LINE}}}
.abt2 .ab2 b{{flex:0 0 28mm;font-family:Mono,monospace;font-weight:700;font-size:6pt;letter-spacing:.08em;color:var(--ac)}}
.abt2 .ab2 span{{font-family:{KO};font-size:8.6pt;color:{INK}}}
.ov .vf{{fill:none;stroke:rgba(255,253,250,.95);stroke-width:.3}}.ov .vfs{{fill:none;stroke:rgba(30,24,18,.3);stroke-width:.9}}
img.flip{{transform:scaleX(-1)}}
.ht,.hd,.bt,.say,.notek,.prob,.prod .nk{{-webkit-text-stroke:.35pt currentColor}}.lab{{-webkit-text-stroke:.2pt currentColor}}  /* 한글 굵은꼴이 없어 획을 더한다 — 최종본은 Pretendard Bold */
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for p, a, g in PAGES:
        ac, band, btx = ACC[a]
        sheets.append(f"<div class='sheet' style='--ac:{ac};--band:{band};--bandtx:{btx}'>{b4.render(p, g)}</div>")
    h = os.path.join(TMP, 'plan_jaju.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU style plan</title><style>{CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_jaju.pdf'), os.path.join(TMP, 'plan_jaju')], check=True)


if __name__ == '__main__':
    main()
