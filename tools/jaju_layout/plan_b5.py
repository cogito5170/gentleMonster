"""JAJU 포트폴리오 — B5: 사례 6(Théophile Desjobert, 제품 디자인 포트폴리오)의 흐름을 B4 에 들인 판.

  python3 tools/jaju_layout/plan_b5.py   ->  docs/jaju_rounding_vmd/layout/plan_b5.pdf

분석과 비교는 docs/jaju_rounding_vmd/ref_case6_desjobert.md. B4 에서 바꾼 것:
  앞부분   표지 → 01 Hello!(사람 사진 + 소개 + 이력 칸) → 02 Contents(번호 · 쪽) → 03 Prologue  — 사례 6 의 Hello · Resume · 목차
           B4 끝의 About 은 Hello 로 옮겼다
  파트 표지 '/01 Observe.' 처럼 빗금 번호 + 마침표 제목 (사례 6 의 '/01 Japan Airline.')
  특징 쪽  10 A room 을 사진 전면 + 반투명 글 상자로 (사례 6 의 'A 350-1000 full cabin.' · 'Coffee flow')
  끝       뒤표지에 'Thank you.' + 연락처 칸 (사례 6 의 Thank you · Contact), 표지 사진을 뒤집는 장치는 그대로
  유령 글자 Hello · Thank you 뒤에 큰 외곽선 글자 (사례 6 의 'Hello!' · 'Resume.' 뒤 회색 큰 글자)
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b4 as b4  # noqa: E402

b3, pe = b4.b3, b4.pe
pc, t, div, photo, e, af, frame = pe.pc, pe.t, pe.div, pe.photo, pe.e, pe.af, pe.frame
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT
NAME = pe.NAME


# ── 01 · Hello! ───────────────────────────────────────────────────────────────────────
def p_hello():
    rows = [('MAJOR', '건축학과 · 학교 · 학년 ____'), ('APPLYING', 'JAJU 라운딩 VMD'),
            ('EXPERIENCE', '판매 · 진열 · 매장 경험 ____'), ('ROUNDING', '출장 · 장기 근무 가능 여부 ____'),
            ('TOOLS', '사진 · 모형 · 스케치업 / 그 밖의 도구 ____'), ('CONTACT', '전화 ____ · 이메일 ____')]
    tbl = ''.join(f"<div class='ab'><b>{a}</b><span>{b}</span></div>" for a, b in rows)
    return ''.join([
        t(10, 14, 200, 40, 'Hello', 'ghost'),
        t(14, 34, 120, 16, 'Hello!', 'h1'),
        t(14, 52, 140, 8, f"I’m {NAME}.", 'imname'),
        t(14, 64, 132, 40, '<p>건축을 공부하며 공간을 읽고,</p><p>사진으로 사람이 멈추는 자리를 기록하고,</p><p>자주 입는 옷으로 조합을 만든다.</p>', 'kb'),
        t(14, 96, 132, 90, tbl, 'abt'),
        photo('FA-05', 176, 22, 109, 166, focus=(0.74, 0.62), zoom=1.5),
        t(176, 190, 109, 5, 'FA-05 — 놀이공원 기념품 노점 앞', 'data'),
    ])


# ── 02 · Contents ─────────────────────────────────────────────────────────────────────
def p_contents():
    rows = [('/01', 'Observe.', '관찰하다 — 사진', '04'), ('/02', 'Contain.', '담다 — 건축', '08'),
            ('/03', 'Fill.', '채우다 — 패션', '11'), ('', 'Proposal.', '한 칸의 진열', '15'), ('', 'Often.', '자주', '16')]
    lst = ''.join(f"<div class='ci'><span class='cn'>{n}</span><span class='ct2'>{w}</span><span class='ck'>{k}</span><span class='cp'>{p}</span></div>"
                  for n, w, k, p in rows)
    return ''.join([
        t(10, 14, 200, 40, 'Contents', 'ghost'),
        t(14, 34, 120, 16, 'Contents.', 'h1'),
        t(14, 70, 140, 120, lst, 'clist'),
        photo('PH-13', 170, 40, 115, 40, focus=(0.5, 0.4)), t(170, 81.5, 115, 4, '/01 OBSERVE', 'data'),
        photo('AR-03', 170, 92, 115, 40, focus=(0.6, 0.5)), t(170, 133.5, 115, 4, '/02 CONTAIN', 'data'),
        photo('FA-02', 170, 144, 115, 40, focus=(0.55, 0.3)), t(170, 185.5, 115, 4, '/03 FILL', 'data'),
    ])


# ── 파트 표지: 빗금 번호 + 마침표 제목 ────────────────────────────────────────────────────
def slash(html, num, word):
    html = html.replace(f'>PART {num}</div>', f'>/0{num}</div>', 1).replace(f'>{word}</div>', f'>{word}.</div>', 1)
    return html.replace("'t pt pn'", "'t pt pn sl'").replace("'t pt dk pn'", "'t pt dk pn sl'")


def p_observe():
    return slash(b4.p_observe(), 1, 'Observe')


def p_fill():
    return slash(pe.p_fill(), 3, 'Fill')


def p_contain():
    return pe.p_contain().replace('>PART 2</div>', '>/02</div>', 1).replace("'t pn2'", "'t pn2 sl2'")


# ── 10 · A room — 사진 전면 + 반투명 글 상자 ─────────────────────────────────────────────
def p_room():
    def living(to, s):
        ey = to(0, 455)[1]
        lx, ly = to(548, 405)
        tx, ty = to(470, 480)
        return (f"<line x1='118' y1='{ey:.1f}' x2='297' y2='{ey:.1f}' class='afl'/><text x='120' y='{ey - 1.4:.1f}' class='afs'>a)  EYE LEVEL</text>"
                + af(lx, ly, 4, 'd)') + frame(tx, ty, 165 * s, 70 * s, 'c)'))

    def hood(to, s):
        cx, cy = to(627, 222)
        return af(cx, cy, 4.5, 'b)')

    keys = ''.join(f"<div class='k'><b>{a}</b> {b}<span>{c}</span></div>" for a, b, c in
                   [('a)', 'Eye level', '눈이 머무는 높이'), ('b)', 'Red point', '빨간 후드 — 시선이 먼저 닿는 곳'),
                    ('c)', 'Set', '식탁 · 의자 · 책 — 한 자리의 조합'), ('d)', 'Light', '스탠드 하나의 빛')])
    return ''.join([
        photo('AR-07', 0, 0, 297, 210, focus=(0.55, 0.55), marks=living),
        div(14, 30, 96, 150, '', 'frost'),
        t(22, 40, 84, 10, 'A room, set like a display.', 'h3'),
        t(22, 56, 82, 30, '<p>방 안에도 진열이 있다.</p><p>눈높이에 무엇을 두고, 어디에 빛을 주고,</p><p>무엇을 한 자리에 모을지.</p>', 'kb'),
        t(22, 86, 82, 60, keys, 'keys'),
        t(22, 168, 82, 6, 'AR-07 거실 · 식당 모형 / AR-08 주방 모형', 'data'),
        photo('AR-08', 196, 132, 89, 56, focus=(0.55, 0.4), marks=hood),
    ])


# ── 뒤표지 — Thank you. ──────────────────────────────────────────────────────────────
def p_back():
    img = photo('COVER', 0, 0, 297, 142, focus=(0.5, 0.39)).replace('<img ', "<img class='flip' ", 1)
    return ''.join([
        div(0, 0, 297, 210, '', 'bg'), img,
        t(14, 8, 120, 5, 'FROM THE INSIDE', 'mast'), t(163, 8, 120, 5, 'JAJU 라운딩 VMD', 'mast r'),
        t(10, 146, 200, 40, 'Thank you', 'ghost'),
        t(14, 156, 160, 20, 'Thank you.', 'cvt2'),
        t(14, 176, 200, 8, '이제 당신은 밖에 있다. 유리의 글자가 바로 읽힌다.', 'cvk'),
        t(183, 158, 100, 30, f"<p>CONTACT</p><p class='nm'>{NAME}</p><p>전화 ____</p><p>이메일 ____</p>", 'contact r'),
    ])


CSS = b4.CSS + """
.ghost{font-family:Young,serif;font-size:96pt;line-height:96pt;color:transparent;-webkit-text-stroke:.35pt rgba(239,231,218,.22);white-space:nowrap}
.imname{font-family:Lora,serif;font-weight:700;font-size:11pt;color:#EFE7DA}
.clist .ci{position:static;display:flex;align-items:baseline;border-bottom:.15mm solid #3a332c;padding:3.4mm 0}
.clist .cn{font-family:Mono,monospace;font-size:8pt;color:#D9773A;width:12mm}
.clist .ct2{font-family:Young,serif;font-size:20pt;color:#EFE7DA;width:52mm}
.clist .ck{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:8pt;color:#9A8F82;flex:1}
.clist .cp{font-family:Mono,monospace;font-size:8pt;color:#9A8F82}
.pn.sl{font-family:Lora,serif;font-style:italic;font-size:20pt;letter-spacing:0;margin-top:-6mm}
.sl2{font-family:Lora,serif;font-style:italic;font-size:18pt;letter-spacing:0}
.frost{background:rgba(24,20,16,.78);border:.15mm solid rgba(239,231,218,.18)}
.h3{font-family:Young,serif;font-size:15pt;line-height:18pt;color:#EFE7DA;white-space:nowrap}
.contact{font-family:Mono,monospace;font-size:6.4pt;line-height:10pt;letter-spacing:.08em;color:#9A8F82}.contact .nm{color:#EFE7DA}
"""

PAGES = [(lambda: b3.p_cover(), ''), (p_hello, ''), (p_contents, ''), (b3.p_prologue, ''), (p_observe, 'g1'),
         (pe.p_grid, 'g1'), (b4.p_detail, 'g1'), (b3.p_reading, 'g1'), (p_contain, ''), (pe.p_collage, ''),
         (p_room, ''), (p_fill, ''), (b4.p_four, ''), (b4.p_items, ''), (pe.p_breakdown, ''), (b4.p_proposal, ''),
         (pe.p_often, ''), (p_back, '')]
PARTS = {4: 'PART 1 OBSERVE', 5: 'PART 1 OBSERVE', 6: 'PART 1 OBSERVE', 7: 'PART 1 OBSERVE', 8: 'PART 2 CONTAIN', 9: 'PART 2 CONTAIN',
         10: 'PART 2 CONTAIN', 11: 'PART 3 FILL', 12: 'PART 3 FILL', 13: 'PART 3 FILL', 14: 'PART 3 FILL'}
FOOT_NUM = re.compile(r"(class='t ft(?: lt)? r'[^>]*>)\d\d(</div>)")


def page(i, p, g):
    html = b4.render(p, g)
    if 0 < i < len(PAGES) - 1:
        if not FOOT_NUM.search(html):  # 바닥 줄이 없는 쪽(Hello · Contents · A room)
            light = p is p_room
            html += (pe.foot_light if light else b4.RAW)(i, PARTS.get(i, ''))
        html = FOOT_NUM.sub(lambda m: f'{m.group(1)}{i:02d}{m.group(2)}', html)
    return html


def main():
    os.makedirs(TMP, exist_ok=True)
    body = ''.join(f"<div class='sheet {g}'>{page(i, p, g)}</div>" for i, (p, g) in enumerate(PAGES))
    h = os.path.join(TMP, 'plan_b5.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B5</title><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b5.pdf'), os.path.join(TMP, 'plan_b5')], check=True)


if __name__ == '__main__':
    main()
