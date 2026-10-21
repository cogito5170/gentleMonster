"""JAJU 포트폴리오 — 변형안 D: 사례 5(VERLAG) 의 구성을 B안 톤으로.

  python3 tools/jaju_layout/plan_d.py   ->  docs/jaju_rounding_vmd/layout/plan_d.pdf

B2(plan_b2.pdf)는 그대로 둔다. 바뀌는 것은 구성이다 (docs/jaju_rounding_vmd/ref_case5_verlag.md 의 V 타입):
  표지          B안 그대로
  01  V1  Editor's Note.     — Prologue 를 편집장 글처럼: 작은 사진 띠 + 세리프 제목 + 국문 · 영문 2단
  02  V4  Observe 01.        — 번호 제목이 접는 선을 넘는다, 작은 사진 하나, 넓은 빈 면
  03  V6  사진 에세이         — 크기가 다른 사진이 접는 선을 넘어 이어진다
  04  V2  글 | 전면 사진       — a)–d) 와 작은 사진 셋 | 빨간 의자 사진 전면
  05  V4  Contain 02.
  06  V6  도시에서 방까지
  07  V2  전면 실내 | 글       — 거실 모형 전면, 주방 모형 작게
  08  V4  Fill 03.
  09  V5  착장 초상            — 한 착장을 판 위에, 아이템 라벨이 접는 선을 넘는다
  10  V3  제품 지면            — 네 착장을 카탈로그 카드로 (No. · 장소 · 아이템)
  11      Proposal            — C안의 3×3 칸 진열 입면
  12  V9  Often—12.           — 세로 제목 + 다시 모으기 + 선언
  뒤  V9  세로 제목의 뒤표지
모든 쪽에 VERLAG 의 메타 블록(작은 글 4–5줄)과 바닥 줄(책 이름 · 쪽 번호). 세리프는 번호 제목 · 큰 제목에만.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, os.path.join(REPO, 'tools/p1_layout'))

import book_b2 as b2  # noqa: E402  (pc.chrome 을 B 톤으로 바꿔 둔다)
import cover_options as co  # noqa: E402
import plan_c as pc  # noqa: E402

OUT, TMP = b2.OUT, b2.TMP
t, div, photo, ring, dash, lab, corners, e = pc.t, pc.div, pc.photo, pc.ring, pc.dash, pc.lab, pc.corners, pc.e
RED = pc.RED
NAME = pc.NAME


def foot(n):
    return (t(12, 200, 160, 4, '<b>FROM THE INSIDE</b>&nbsp;&nbsp;—&nbsp;&nbsp;Visual Merchandiser Portfolio', 'ft')
            + t(245, 200, 40, 4, f'{NAME}&nbsp;&nbsp;<b>{n:02d}</b>', 'ft r'))


def meta(x, y, lines, w=44):
    return t(x, y, w, 30, ''.join(f'<p>{"<b>" + l + "</b>" if i == 0 else l}</p>' for i, l in enumerate(lines)), 'meta')


pc.chrome = lambda n, word: foot({15: 11}.get(n, n))
pc.gutter = lambda: ''


# ── 01 · Editor's Note. (V1) ───────────────────────────────────────────────────────────
def p_editor():
    ko = ''.join(f'<p>{e(l)}</p>' for l in pc.LEAD_KO)
    return ''.join([
        photo('COVER', 12, 16, 84, 44, focus=(0.13, 0.4)), div(96, 16, 44.5, 44, '', 'panel'),
        meta(12, 68, ['Editor’s Note', 'From the inside', 'JAJU 라운딩 VMD', '2026', NAME]),
        t(156.5, 16, 128.5, 20, 'Editor’s Note.', 'disp'),
        t(156.5, 44, 78, 140, ko, 'col wrap'),
        t(238, 44, 47, 140, f'<p>{e(pc.LEAD_EN)}</p>', 'colen wrap'),
        foot(1),
    ])


# ── V4 · 번호 제목 ─────────────────────────────────────────────────────────────────────
def chapter(n, num, name, ko, pid, focus, meta_lines, s1, s2):
    return ''.join([
        photo(pid, 12, 34, 52, 66, focus=focus),
        meta(12, 106, meta_lines),
        t(56, 112, 240, 70, f"{name} <span>{num}.</span>", 'huge'),
        t(170, 34, 74, 30, f'<p>{s1}</p><p>{s2}</p>', 'lead2 wrap'),
        t(170, 58, 74, 6, ko, 'meta'),
        foot(n),
    ])


def p_obs():
    return chapter(2, '01', 'Observe', '관찰하다 — 사진', 'PH-04', (0.6, 0.5),
                   ['Chapter 01', '사진 · Photography', '17 photographs', '관찰하다'],
                   '나는 사람들이 어디에서 걸음을 멈추는지 본다.', '멈춘 자리에는 늘 무언가가 놓여 있었다.')


def p_con():
    return chapter(5, '02', 'Contain', '담다 — 건축', 'AR-03', (0.62, 0.5),
                   ['Chapter 02', '건축 · Architecture', '모형 · 렌더 10', '담다'],
                   '멈춘 자리에는 늘 틀이 있었다.', '무엇을 채우고 무엇을 비울지가 그 안의 하루를 정한다.')


def p_fil():
    return chapter(8, '03', 'Fill', '채우다 — 패션', 'FA-02', (0.42, 0.45),
                   ['Chapter 03', '패션 · Fashion', '착장 5', '채우다'],
                   '웃음이 머문 곳에는 늘 조합이 있었다.', '나는 자주 입는 옷으로 빈 자리를 채운다.')


def cap(x, y, w, a, b, pid):
    return t(x, y, w, 8, f"<p><b>{a}</b>&nbsp;&nbsp;{b}<span class='pid'>{pid}</span></p>", 'gc')


# ── 03 · 사진 에세이 (V6) ──────────────────────────────────────────────────────────────
def p_essay():
    return ''.join([
        photo('PH-06', 12, 16, 78, 52), cap(12, 69.5, 78, 'Stop', '메뉴판 앞', 'PH-06'),
        photo('PH-11', 94, 16, 108, 70, focus=(0.5, 0.5)), cap(94, 87.5, 108, 'Pause', '가게 앞, 앉은 사람', 'PH-11'),
        photo('PH-17', 206, 16, 79, 52, focus=(0.37, 0.6)), cap(206, 69.5, 79, 'Rest', '벤치의 두 사람', 'PH-17'),
        meta(12, 82, ['Where people stop', '사진 · 6 / 17', '멈춤 → 반복 → 색']),
        t(12, 104, 76, 40, '<p>멈춘 자리를 모아 보면 사람이 모이고, 같은 것이 되풀이되고, 색과 선이 이어진다.</p>', 'col wrap'),
        photo('PH-09', 94, 100, 108, 62, focus=(0.6, 0.6)), cap(94, 163.5, 108, 'Repeat', '드럼통 기차와 반영', 'PH-09'),
        photo('PH-16', 206, 84, 79, 52, focus=(0.4, 0.6)), cap(206, 137.5, 79, 'Colour', '파스텔 돌담', 'PH-16'),
        photo('PH-03', 206, 150, 79, 30, focus=(0.3, 0.55)), cap(206, 181.5, 79, 'Rhythm', '노 젓는 여섯 사람', 'PH-03'),
        photo('PH-12', 12, 150, 76, 31, focus=(0.5, 0.6)), cap(12, 182.5, 76, 'Flow', '육교 아래 곡선', 'PH-12'),
        foot(3),
    ])


# ── 04 · 글 | 전면 사진 (V2) ───────────────────────────────────────────────────────────
def p_detail():
    def chair(to, s):
        cx, cy = to(1072, 578)
        return ring(cx, cy, 6) + lab(cx - 8, cy - 6, 'a)', 'end')

    def pink(to, s):
        cx, cy = to(687, 545)
        return ring(cx, cy, 3) + lab(cx + 4, cy + 1, 'b)')

    def sig(to, s):
        cx, cy = to(880, 94)
        return ring(cx, cy, 2.6) + lab(cx + 3.8, cy + 1, 'c)')

    def gap(to, s):
        x0, y0 = to(390, 230)
        return dash(x0, y0, 950 * s, 300 * s) + lab(x0 + 1, y0 - 1.2, 'd)')

    keys = ''.join(f"<div class='k'><b>{a}</b> {b}<span>{c}</span></div>" for a, b, c in
                   [('a)', 'Red chair', '파란 바다, 모서리의 빨강'), ('b)', 'Pink', '수십 명 가운데 한 사람'),
                    ('c)', 'Signal', '어둠 속 빨간 신호'), ('d)', 'Through the gap', '틈 너머의 사람들')])
    return ''.join([
        meta(12, 16, ['What made me stop', '사진 · 4 / 17', 'a)–d) 시선이 먼저 닿은 곳']),
        t(12, 42, 128, 14, 'What made me stop.', 'disp2'),
        t(12, 60, 120, 30, '<p>넓은 장면에서도 눈은 한 점에 먼저 간다. 진열도 같다 — 시선이 먼저 닿을 한 점을 정하고, 그 점이 놓일 자리를 만든다.</p>', 'col wrap'),
        t(12, 88, 128, 50, keys, 'keys'),
        photo('PH-01', 12, 146, 40, 34, focus=(0.458, 0.64), zoom=3.0, marks=pink),
        photo('PH-08', 56, 146, 40, 34, focus=(0.62, 0.3), zoom=1.6, marks=sig),
        photo('PH-13', 100, 146, 40.5, 34, focus=(0.55, 0.45), marks=gap),
        photo('PH-05', 148.5, 0, 148.5, 210, focus=(0.93, 0.6), marks=chair),
        foot(4),
    ])


# ── 06 · 도시에서 방까지 (V6) ──────────────────────────────────────────────────────────
def p_city():
    def red(to, s):
        cx, cy = to(1525, 715)
        return ring(cx, cy, 3.6)

    def yard(to, s):
        x0, y0 = to(380, 140)
        return dash(x0, y0, 330 * s, 400 * s)

    return ''.join([
        meta(12, 16, ['From the city to the room', '건축 · 5 / 10', '도시 → 마당 → 길 → 집']),
        t(12, 42, 128, 14, 'From the city to the room.', 'disp2'),
        t(12, 60, 124, 20, '<p>도시에서 마당으로, 마당에서 길과 집으로. 틀을 좁혀 갈수록 그 안의 하루가 보인다.</p>', 'col wrap'),
        photo('AR-09', 12, 80, 160, 70, marks=red), cap(12, 151.5, 160, 'City', '도시의 광장 — 렌더', 'AR-09'),
        photo('AR-06', 12, 160, 60, 32, focus=(0.5, 0.42), marks=yard), cap(76, 162, 60, 'Courtyard', '건물 사이를 비운 마당', 'AR-06'),
        photo('AR-05', 178, 16, 107, 46, focus=(0.45, 0.5)), cap(178, 63.5, 107, 'Path', '두 매스를 잇는 회랑', 'AR-05'),
        photo('AR-10', 178, 80, 52, 70), cap(178, 151.5, 52, 'House', '골목 언덕의 집', 'AR-10'),
        photo('AR-02', 234, 80, 51, 70, focus=(0.62, 0.45)), cap(234, 151.5, 51, 'Hollow', '도시 아래 단면', 'AR-02'),
        t(178, 170, 107, 10, '모형 · 렌더 — 건축학과 작업. 프로젝트 이름 · 학년 ____', 'meta'),
        foot(6),
    ])


# ── 07 · 전면 실내 | 글 (V2, VERLAG 의 짙은 실내 쪽) ──────────────────────────────────────
def p_room():
    def living(to, s):
        ey = to(0, 455)[1]
        lx, ly = to(548, 405)
        tx, ty = to(470, 480)
        return (f"<line x1='0' y1='{ey:.1f}' x2='148.5' y2='{ey:.1f}' class='gl'/>" + lab(14, ey - 1.4, 'a)  Eye level')
                + ring(lx, ly, 3.4) + lab(lx + 4.6, ly + 1, 'd)') + dash(tx, ty, 165 * s, 70 * s) + lab(tx, ty + 70 * s + 3.6, 'c)'))

    def hood(to, s):
        cx, cy = to(627, 222)
        return ring(cx, cy, 4.6) + lab(cx + 6, cy + 1, 'b)')

    keys = ''.join(f"<div class='k'><b>{a}</b> {b}<span>{c}</span></div>" for a, b, c in
                   [('a)', 'Eye level', '눈이 머무는 높이'), ('b)', 'Red point', '빨간 후드'),
                    ('c)', 'Set', '식탁 · 의자 · 책의 조합'), ('d)', 'Light', '스탠드 하나의 빛')])
    return ''.join([
        photo('AR-07', 0, 0, 148.5, 210, focus=(0.52, 0.55), marks=living),
        meta(156.5, 16, ['A room, set like a display', '건축 · 실내 모형', 'AR-07 · AR-08']),
        t(156.5, 42, 128, 14, 'A room, set like a display.', 'disp2'),
        t(156.5, 60, 72, 50, '<p>방 안에도 진열이 있다. 눈높이에 무엇을 두고, 어디에 빛을 주고, 무엇을 한 자리에 모을지.</p>', 'col wrap'),
        t(234, 60, 52, 60, keys, 'keys'),
        photo('AR-08', 156.5, 116, 128.5, 66, focus=(0.55, 0.4), marks=hood),
        cap(156.5, 183.5, 128.5, 'Red point', '주방 모형', 'AR-08'),
        foot(7),
    ])


# ── 09 · 착장 초상 (V5) ────────────────────────────────────────────────────────────────
def p_portrait():
    x0, y0, w, h = 58, 16, 90.5, 178
    W, H = 1202, 1500
    s = max(w / W, h / H)
    ox = min(0, max(w - W * s, w / 2 - 0.53 * W * s))
    pts = [('Hair', '짧고 단정하게', 610, 540, 64), ('Coat', '검정 오버핏 롱코트', 640, 930, 96),
           ('Trousers', '네이비 와이드 팬츠', 640, 1370, 140), ('Shoes', '회색 스니커즈', 600, 1455, 170)]
    svg = ''
    for en, ko, px, py, ly in pts:
        cx, cy = x0 + ox + px * s, y0 + py * s
        svg += f"<circle cx='{cx:.2f}' cy='{cy:.2f}' r='1' class='dotr'/><polyline points='{cx:.2f},{cy:.2f} 154,{ly} 160,{ly}' class='gl2' fill='none'/>"
        svg += f"<text x='162' y='{ly + 1}' class='lb2'><tspan font-weight='700'>{en}</tspan>  {ko}</text>"
    return ''.join([
        meta(12, 16, ['The process of combining', '패션 · FA-04', '가게 앞 · 저녁', '검정 · 네이비 · 회색']),
        t(30, 120, 80, 6, '착장 한 벌을 아이템으로', 'vt2'),
        div(x0, y0, w, h, '', 'panel'),
        photo('FA-04', x0, y0, w, h, focus=(0.53, 0.5)),
        div(0, 0, 297, 210, f"<svg class='ov' viewBox='0 0 297 210'>{svg}</svg>", ''),
        t(156.5, 16, 128, 14, 'The process of combining.', 'disp2'),
        t(156.5, 32, 124, 20, '<p>무엇을 고르고 무엇을 뺐는지가 조합을 만든다.</p>', 'ital wrap'),
        photo('FA-03', 226, 110, 59, 72, focus=(0.6, 0.5)),
        t(226, 183.5, 59, 8, '<p><b>Back</b>&nbsp;&nbsp;손님은 마네킹의 등을 먼저 본다</p>', 'gc'),
        foot(9),
    ])


# ── 10 · 제품 지면 (V3) — 네 착장을 카탈로그 카드로 ─────────────────────────────────────
def p_catalog():
    cards = [('FA-05', (0.72, 0.6), '02', 'Park, afternoon', '놀이공원 · 오후', '베이지 재킷 · 회색 팬츠'),
             ('FA-04', (0.53, 0.55), '03', 'Shop front, evening', '가게 앞 · 저녁', '검정 롱코트 · 네이비 팬츠'),
             ('FA-03', (0.6, 0.5), '04', 'Seaside rocks', '바닷가 바위', '회색 니트 · 연청 데님')]
    o = [photo('FA-01', 12, 16, 84, 110, focus=(0.55, 0.62)),
         meta(100, 16, ['No. 01', 'Riverside, night', '강변 · 밤', '올리브 롱 파카', '검정 셔츠 · 흰 티'], w=40),
         t(12, 134, 124, 14, 'Four places, four outfits.', 'disp2'),
         t(12, 152, 124, 20, '<p>나는 그날 갈 장소에 옷의 톤을 맞춘다. 장소가 틀이라면, 옷은 그 틀을 채우는 조합이다.</p>', 'col wrap')]
    for i, (pid, f, n, en, ko, items) in enumerate(cards):
        x = 156.5 + i * 43.5
        o.append(photo(pid, x, 16, 40, 56, focus=f))
        o.append(meta(x, 76, [f'No. {n}', en, ko, items], w=40))
    pal = ''.join(f"<div><i style='background:{c}'></i><span>{w}</span></div>" for c, w in
                  [('#1c1c1a', '검정'), ('#4f4a2c', '올리브'), ('#cbbfae', '베이지'), ('#8f8b84', '회색')])
    o += [meta(156.5, 130, ['Palette', '네 장소, 네 가지 색 안에서']), div(156.5, 148, 128.5, 14, pal, 'pal'), foot(10)]
    return ''.join(o)


# ── 12 · Often—12. (V9) ───────────────────────────────────────────────────────────────
def p_often():
    grid = [('COVER', (0.75, 0.45)), ('PH-04', (0.6, 0.5)), ('AR-03', (0.6, 0.5)), ('AR-07', (0.5, 0.55)), ('FA-02', (0.42, 0.45)), ('PH-05', (0.93, 0.7))]
    o = []
    for i, (pid, f) in enumerate(grid):
        r, c = divmod(i, 2)
        o.append(photo(pid, 12 + c * 66, 16 + r * 60, 62.5, 56, focus=f))
    return ''.join(o + [
        t(178, 16, 220, 40, 'Often—12.', 'vt'),
        meta(222, 16, ['Why often?', '“자주 쓸수록, 최상의 삶.”', '그렇다면 진열은', '무엇을 자주 해야 할까.'], w=62),
        t(222, 112, 64, 60, '<p>자주 보고,</p><p>자주 담고,</p><p><span class=\'red\'>자주</span> 채운다.</p>', 'big2'),
        t(222, 160, 64, 10, 'I look often. I hold often. I fill often.', 'meta'),
        foot(12),
    ])


# ── 뒤표지 (V9) ───────────────────────────────────────────────────────────────────────
def p_back():
    return ''.join([
        photo('COVER', 172, 34, 70, 100, focus=(0.13, 0.4)),
        t(262, 16, 200, 30, 'FROM THE INSIDE.', 'vt vtb'),
        t(172, 140, 76, 10, 'No. JAJU', 'disp2'),
        meta(172, 156, ['Outside', '이제 당신은 밖에 있다.', NAME, 'Visual Merchandiser', '연락처 ____'], w=76),
    ])


CSS = b2.DARK + f"""
.ft{{font-size:5.6pt;color:#666;letter-spacing:.05em;white-space:nowrap}}.ft b{{color:#aaa}}
.meta{{font-size:5.8pt;line-height:8.6pt;color:#8a8a8a}}.meta b{{color:#fff}}.meta p{{white-space:nowrap}}
.panel{{background:#1a1a1a}}
.wrap p{{white-space:normal}}.wrap{{word-break:keep-all}}

.disp{{font-family:Crimson,serif;font-size:34pt;line-height:34pt;color:#fff}}
.disp2{{font-family:Crimson,serif;font-size:20pt;line-height:22pt;color:#fff;white-space:nowrap}}
.huge{{font-family:Crimson,serif;font-size:120pt;line-height:110pt;color:#fff;white-space:nowrap;letter-spacing:-.02em}}.huge span{{color:{RED}}}
.lead2{{font-size:9pt;line-height:14pt;font-weight:700;color:#fff}}
.col{{font-size:8.6pt;line-height:14pt;color:#cfcfcf}}.colen{{font-size:6.6pt;line-height:10pt;color:#8a8a8a}}
.ital{{font-family:Crimson,serif;font-style:italic;font-size:13pt;line-height:17pt;color:#cfcfcf}}
.vt{{font-family:Crimson,serif;font-size:80pt;line-height:80pt;color:#fff;white-space:nowrap;transform:rotate(90deg);transform-origin:0 0;left:auto}}
.vt2{{font-size:6pt;color:#8a8a8a;white-space:nowrap;transform:rotate(-90deg);transform-origin:0 0}}
.big2{{font-size:22pt;line-height:30pt;font-weight:700;color:#fff}}
.gc{{font-size:5.8pt;color:#8a8a8a;white-space:nowrap}}.gc b{{color:#fff}}
.keys .k{{font-size:7.6pt;line-height:10pt;margin-bottom:2.2mm;color:#fff}}
.vt.vtb{{font-size:46pt;line-height:46pt}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    parts = [b2.render('d_cover', [co.b_cover()], co.CSS)]
    parts.append(b2.render('d_book', [p_editor(), p_obs(), p_essay(), p_detail(), p_con(), p_city(), p_room(), p_fil(),
                                      p_portrait(), p_catalog(), pc.p_proposal(), p_often(), p_back()], CSS))
    out = os.path.join(OUT, 'plan_d.pdf')
    subprocess.run(['pdfunite', *parts, out], check=True)
    print('wrote', out)


if __name__ == '__main__':
    main()
