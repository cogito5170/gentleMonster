"""JAJU 포트폴리오 — 자주 스타일 안 2: 자주 스타일 안의 쪽 순서 · 틀은 그대로, 글 · 글자 크기 · 위치 · 레이아웃만 다듬은 판.

  python3 tools/jaju_layout/plan_jaju2.py   ->  docs/jaju_rounding_vmd/layout/plan_jaju2.pdf

사용자: "포트폴리오 사례를 참고하여 텍스트, 텍스트 크기, 위치, 레이아웃 등의 부족한 점을 분석하라. 분석을 바탕으로 임의 판단 하에 보완하라."
분석: docs/jaju_rounding_vmd/jaju_type_layout_gaps.md
  글자 크기   9pt 아래 크기가 일곱 가지(5.2–8.6pt) → 다섯 단계로: 첫 화면 22 · 제목 20 · 리드 9.4 · 본문 8.6 · 캡션 7.4 · 표지 글 6.4
  머리        위 여백 12 → 14mm, 설명 한 줄(150mm) → 두 줄로 끊어 가운데
  첫 화면     색 띠 50 → 38mm (사진 · 판을 키움)
  옆 글 칸    04 · 08 의 글 칸 시작을 182mm 로 맞춤
  캡션        고정폭 5.6pt 데이터 → 7.4pt 캡션 (10 · 15)
  12          ⊕ 표시에 번호 → 목록과 이어짐
  11          상품 칸을 키워 아래 빈 곳을 메움
  14 · 15     긴 가운데 문단을 세 줄로, 이름을 키움
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_jaju as pj  # noqa: E402

b4, pe = pj.b4, pj.pe
t, div, photo, e, af, frame = pj.t, pj.div, pj.photo, pj.e, pj.af, pj.frame
framed, label, heading, chip, checks, foot, crop, mean_hex = pj.framed, pj.label, pj.heading, pj.chip, pj.checks, pj.foot, pj.crop, pj.mean_hex
OUT, TMP, PRINT, NAME = pj.OUT, pj.TMP, pj.PRINT, pj.NAME


# ── 공통 부품 고침 ──────────────────────────────────────────────────────────────────
def two_lines(s):
    """한 줄로 긴 설명을 첫 마침표에서 끊는다 (가운데 정렬 줄 길이 ≤ 약 110mm)."""
    return s.replace('. ', '.<br>', 1) if '<br>' not in s else s


def head(y, lab, hd, ds, w=240):
    x, y = (297 - w) / 2, y + 2
    return label(x, y, w, lab) + heading(x, y + 5.5, w, hd) + pj.desc(x, y + 17, w, two_lines(ds))


def hero(pid, focus, mark, title, sub, band_t, band_s, n=None, part='', vf=False, right=True, flip=False, zoom=1.0):
    H = 172  # 색 띠 38mm
    px, lx = (118, 0) if right else (0, 179)
    img = photo(pid, px, 0, 179, H, focus=focus, zoom=zoom)
    if flip:
        img = img.replace('<img ', "<img class='flip' ", 1)
    o = [div(lx, 0, 118, H, '', 'panel'), img,
         t(lx + 10, 42, 98, 5, mark, 'mark c'),
         t(lx + 5, 54, 108, 46, title, 'ht c'),
         div(lx + 58.8, 106, .2, 12, '', 'vline'),
         t(lx + 8, 124, 102, 24, sub, 'hs c wrap'),
         div(0, H, 297, 210 - H, '', 'band'),
         t(20, 179, 257, 7, band_t, 'bt c'),
         t(30, 187, 237, 12, band_s, 'bs c wrap')]
    if vf:
        o.append(pj.viewfinder(px + 8, 8, px + 171, H - 8))
    if n is not None:
        o.append(t(14, 203, 160, 4, f"FROM THE INSIDE{('&nbsp;&nbsp;·&nbsp;&nbsp;' + part) if part else ''}", 'ft bf'))
        o.append(t(243, 203, 40, 4, f'{n:02d}', 'ft bf r'))
    return ''.join(o)


pj.head, pj.hero = head, hero


def plus(x, y, n):
    return div(x - 2.4, y - 2.4, 4.8, 4.8, str(n), 'plus')


# ── 04 · 글 칸을 182mm 로 ───────────────────────────────────────────────────────────
def p_detail():
    html = pj.p_detail()
    html = re.sub(r"left:188mm;top:([\d.]+)mm;width:9\dmm;", lambda m: f"left:182mm;top:{m.group(1)}mm;width:100mm;", html)
    return html.replace("left:188mm;", "left:182mm;")


# ── 08 · A room ─────────────────────────────────────────────────────────────────────
def p_room():
    def living(to, s):
        ey = to(0, 455)[1]
        lx, ly = to(548, 405)
        tx, ty = to(470, 480)
        return (f"<line x1='0' y1='{ey:.1f}' x2='156' y2='{ey:.1f}' class='afl'/><text x='2' y='{ey - 1.4:.1f}' class='afs'>a)  EYE LEVEL</text>"
                + af(lx, ly, 4, 'd)') + frame(tx, ty, 165 * s, 70 * s, 'c)'))

    def hood(to, s):
        return af(*to(627, 222), 4.5, 'b)')

    return ''.join([
        framed('AR-07', 18, 20, 156, 118, focus=(0.55, 0.55), marks=living),
        framed('AR-08', 92, 126, 82, 54, 1.5, focus=(0.55, 0.4), marks=hood),
        label(182, 26, 100, 'CONTAIN NOTE', 'l'),
        heading(182, 33, 100, '방 안에도 <em>진열</em>이 있다', 'l'),
        pj.desc(182, 47, 98, '눈높이에 무엇을 두고, 어디에 빛을 주고,<br>무엇을 한 자리에 모을지.', 'l'),
        chip(182, 66, 'ROOM'),
        checks(182, 74, 100, [('a) Eye level', '눈이 머무는 높이'), ('b) Red point', '빨간 후드 — 시선이 먼저 닿는 곳'),
                              ('c) Set', '식탁 · 의자 · 책 — 한 자리의 조합'), ('d) Light', '스탠드 하나의 빛')]),
        t(182, 172, 100, 12, '<p>AR-07 거실 · 식당 모형</p><p>AR-08 주방 모형</p>', 'cap'),
        foot(8, 'PART 2 CONTAIN'),
    ])


# ── 10 · Four places — 캡션을 읽히는 크기로 ─────────────────────────────────────────
def p_four():
    three = [('FA-04', (0.53, 0.55), '02', '저녁', '가게 앞', 104, 52, 1), ('FA-05', (0.72, 0.6), '03', '오후', '공원', 162, 46, -1),
             ('FA-03', (0.6, 0.5), '04', '맑은 날', '바닷가 바위', 220, 54, .8)]
    o = [head(12, 'STYLING NOTE', '네 장소, <em>네 벌</em>', '나는 그날 갈 장소에 옷의 톤을 맞춘다. 장소가 틀이라면, 옷은 그 틀을 채우는 조합이다.'),
         framed('FA-01', 22, 50, 66, 116, focus=(0.55, 0.6)),
         t(22, 170, 70, 6, '<p><b>N°01</b>&nbsp;&nbsp;밤 · 강변</p>', 'cap')]
    for pid, f, n, tod, place, x, y, r in three:
        o.append(framed(pid, x, y, 50, 68, r, focus=f))
        o.append(t(x, y + 72, 54, 6, f'<p><b>N°{n}</b>&nbsp;&nbsp;{tod} · {place}</p>', 'cap'))
    sw = ''.join(f"<div><i style='background:{h}'></i><b>{name}</b><span>{h}</span></div>"
                 for h, name in ((mean_hex(pid, box), name) for pid, box, name in b4.OUTFITS))
    o += [chip(104, 150, 'PALETTE'), t(126, 150.2, 120, 5, '착장 사진에서 잰 색', 'notek'),
          div(104, 158, 176, 24, sw, 'pal2'), foot(10, 'PART 3 FILL')]
    return ''.join(o)


# ── 11 · Items — 칸을 키움 ──────────────────────────────────────────────────────────
def p_items():
    o = [head(12, 'ITEM', '자주 입는 <em>여섯 가지</em>', '조합은 아이템에서 시작한다. 자주 입는 여섯 가지를 진열하듯 하나씩 놓았다.')]
    w, h, gap, x0 = 40.5, 74, 3.4, 18.5
    for i, (pid, (cx, cy), span, en, ko) in enumerate(b4.ITEMS):
        x = x0 + i * (w + gap)
        half = span / 2
        hx = mean_hex(pid, (int(cx - half / 2), int(cy - half / 2), int(cx + half / 2), int(cy + half / 2)))
        o.append(div(x, 52, w, h, '', 'card'))
        o.append(crop(pid, x + 3, 55, w - 6, h - 6, cx, cy, span))
        o.append(t(x, 130, w, 16, f"<p class='nk'>{ko}</p><p class='ne'>{en}</p><p class='nh'><i style='background:{hx}'></i>{hx}</p>", 'prod c'))
    o += [chip(18.5, 166, 'NOTE'), t(34, 166.2, 220, 5, '사진은 착장 사진(FA-01–05)에서 잘라 냈고, 색은 그 자리 픽셀의 평균이다.', 'notek'),
          foot(11, 'PART 3 FILL')]
    return ''.join(o)


# ── 12 · Breakdown — 번호 붙은 ⊕ ─────────────────────────────────────────────────────
def p_breakdown():
    x0, y0, w, h = 26, 16, 96, 178
    W, H = 1202, 1500
    s = max(w / W, h / H)
    ox = min(0, max(w - W * s, w / 2 - 0.53 * W * s))
    oy = min(0, max(h - H * s, h / 2 - 0.5 * H * s))
    pts = [(610, 540), (640, 930), (640, 1370), (600, 1455)]
    return ''.join([
        framed('FA-04', x0, y0, w, h, focus=(0.53, 0.5)),
        ''.join(plus(x0 + ox + px * s, y0 + oy + py * s, i + 1) for i, (px, py) in enumerate(pts)),
        label(140, 24, 140, 'STYLING NOTE', 'l'),
        heading(140, 31, 140, '손님은 <em>등</em>을 먼저 본다', 'l'),
        t(140, 45, 140, 6, 'Front, or back? Inside the store, people meet the mannequin’s back first.', 'en l'),
        pj.desc(140, 53, 130, '매장 안의 손님은 마네킹의 등을 먼저 본다.<br>그래서 나는 등을 먼저 입힌다 — 니트의 결, 어깨에서 떨어지는 품.', 'l'),
        chip(140, 72, 'APPAREL'),
        checks(140, 80, 52, [('1 HAIR', '짧고 단정하게'), ('2 COAT', '검정 오버핏 롱코트'), ('3 TROUSERS', '네이비 와이드 팬츠'),
                             ('4 SHOES', '회색 스니커즈')]),
        framed('FA-03', 202, 84, 78, 82, 1.2, focus=(0.6, 0.5)),
        t(202, 170, 80, 6, '<p><b>FA-03</b>&nbsp;&nbsp;등과 니트의 결</p>', 'cap'),
        foot(12, 'PART 3 FILL'),
    ])


# ── 14 · Often — 가운데 문단을 짧은 줄로 ─────────────────────────────────────────────
def p_often():
    row = [('COVER', (0.76, 0.45), 'FROM THE INSIDE'), ('PH-04', (0.6, 0.5), 'OBSERVE'), ('AR-03', (0.6, 0.5), 'CONTAIN'),
           ('AR-07', (0.5, 0.55), 'A ROOM'), ('FA-02', (0.45, 0.45), 'FILL')]
    o = [t(28, 18, 241, 12, "자주 보고, 자주 담고, <em>자주</em> 채운다.", 'hd big c'),
         t(28, 32, 241, 5, 'O F T E N', 'spaced c'),
         t(48, 41, 201, 26, '<p>JAJU 는 “자주 쓸수록, 최상의 삶”이라고 말한다.</p><p>진열도 자주 볼수록 정확해진다.</p>'
                            '<p>나는 매장을 돌며 자주 보고, 그 자리에 맞게 담고,</p><p>손님의 하루에 맞는 조합으로 채우는 VMD 가 되려 한다.</p>', 'pro c')]
    for i, (pid, f, w) in enumerate(row):
        x = 22 + i * 52.5
        o.append(framed(pid, x, 80, 46, 70, (-1, .8, -.5, 1, -.8)[i], focus=f))
        o.append(t(x, 154, 48, 6, f'<p><b>N°{i + 1:02d}</b>&nbsp;&nbsp;{w}</p>', 'cap c'))
    o += [t(58, 168, 181, 16, 'JAJU says, “the more often you use it, the better life becomes.” A display, too, becomes more precise the more often it is looked at. '
                             'I want to be a VMD who looks often, holds each place as it is, and fills it with what fits the day.', 'en c wrap'),
          foot(14)]
    return ''.join(o)


# ── 15 · About — 이름을 키움, 캡션 ───────────────────────────────────────────────────
def p_about():
    rows = [('MAJOR', '건축학과 · 학교 · 학년 ____'), ('APPLYING', 'JAJU 라운딩 VMD'),
            ('EXPERIENCE', '판매 · 진열 · 매장 경험 ____'), ('ROUNDING', '출장 · 장기 근무 가능 여부 ____'),
            ('IN THIS BOOK', '사진 17 · 건축 작업 10 · 착장 5 — 모두 직접 찍고 만든 것'),
            ('CONTACT', '전화 ____ · 이메일 ____'), ('IMAGE CREDIT', '표지 이미지 ____ (직접 촬영 / 출처)')]
    tbl = ''.join(f"<div class='ab2'><b>{a}</b><span>{b}</span></div>" for a, b in rows)
    return ''.join([
        framed('FA-05', 26, 18, 96, 164, -1, focus=(0.74, 0.62), zoom=1.5),
        t(26, 186, 96, 6, '<p><b>FA-05</b>&nbsp;&nbsp;놀이공원 기념품 노점 앞</p>', 'cap'),
        label(140, 24, 140, 'ABOUT', 'l'),
        heading(140, 31, 140, '사람이 <em>멈추는 자리</em>를 보는 사람', 'l'),
        t(140, 45, 140, 8, f'I’m {NAME}.', 'imname2'),
        pj.desc(140, 55, 130, '사람이 멈추는 자리를 보고,<br>그 자리에 맞는 조합을 세우는 사람이 되려 한다.', 'l'),
        t(140, 76, 140, 100, tbl, 'abt2'),
        foot(15),
    ])


SWAP = {pj.p_detail: p_detail, pj.p_room: p_room, pj.p_four: p_four, pj.p_items: p_items, pj.p_breakdown: p_breakdown,
        pj.p_often: p_often, pj.p_about: p_about}
PAGES = [(SWAP.get(p, p), a, g) for p, a, g in pj.PAGES]

KO, INK, SUB = pj.KO, pj.INK, pj.SUB
CSS = pj.CSS + f"""
/* 글자 크기 다섯 단계 — 첫 화면 22 · 제목 20 · 리드 9.4 · 본문 8.6 · 캡션 7.4 · 표지 글 6.4 (pt) */
.ht{{font-size:22pt;line-height:31pt}}
.hd{{font-size:20pt;line-height:26pt}}.hd.big{{font-size:22pt;line-height:28pt}}
.ds{{font-size:9.4pt;line-height:14.5pt}}.hs{{font-size:9pt;line-height:14.5pt}}
.en,.hs .en,.bs .en{{font-size:8.6pt;line-height:13pt}}
.bt{{font-size:12pt}}.bs{{font-size:9pt;line-height:13pt}}.bs .cr{{font-size:5.6pt}}
.lab{{font-size:7pt}}.mark{{font-size:8.6pt}}
.cap{{font-size:7.4pt;line-height:11pt}}.cap b{{font-size:8.2pt}}
.data{{font-size:6.4pt;line-height:10pt}}.chip{{font-size:6.6pt}}.ft{{font-size:6pt}}
.cks .ck b{{font-size:8.6pt}}.cks .ck span{{font-size:8.2pt}}.cks .ck:before{{font-size:8.4pt}}.cks .ck{{padding:1.9mm 0}}
.say{{font-size:11pt;line-height:18pt}}.notek{{font-size:9pt}}
.pro{{font-size:9.4pt;line-height:16pt}}.prob{{font-size:10pt}}
.part .pk{{font-size:8pt}}
.pal2 b{{font-size:6.6pt}}.pal2 span{{font-size:6.4pt}}
.prod .nk{{font-size:8.8pt}}.prod .ne,.prod .nh{{font-size:6.4pt}}
.stx{{font-size:7.2pt}}.ribbon{{font-size:6.8pt}}.cell2{{font-size:6.2pt}}
.abt2 .ab2 b{{font-size:6.8pt}}.abt2 .ab2 span{{font-size:9.4pt}}
.imname2{{font-family:Lora,serif;font-weight:700;font-size:12pt;color:{INK};white-space:nowrap}}
.plus{{font-size:7.4pt;line-height:4.2mm}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for p, a, g in PAGES:
        ac, band, btx = pj.ACC[a]
        sheets.append(f"<div class='sheet' style='--ac:{ac};--band:{band};--bandtx:{btx}'>{b4.render(p, g)}</div>")
    h = os.path.join(TMP, 'plan_jaju2.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU style plan 2</title><style>{CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_jaju2.pdf'), os.path.join(TMP, 'plan_jaju2')], check=True)


if __name__ == '__main__':
    main()
