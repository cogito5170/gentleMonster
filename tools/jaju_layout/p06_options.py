"""JAJU 포트폴리오 6쪽 What made me stop. — 레이아웃 세 안 (315 × 195, B20 의 격자 · 바닥 줄).

  python3 tools/jaju_layout/p06_options.py   ->  docs/jaju_rounding_vmd/layout/p06_options.pdf (3쪽: A · B · C)

사용자: "6쪽의 레이아웃 배치를 다시 진행한다. 첨부된 이미지(감독 Jason Bergh 포트폴리오 웹사이트)를 바탕으로 레이아웃을 재작성하라.
2-2 세션에서 현재 작성 중인 스토리를 반영할 것. 포트폴리오 사례를 참고하여 다른 레이아웃으로 파생 허용. 3가지 안."
글: 2-2 세션 p06_story.md rev4(awesome-keller 75557a6) — 포인트: 주변과 어울리면서도 한 가지가 다른 것, '내가 옷을 입을 때'.
참고 사이트에서 가져온 것:
  · 가는 세리프 제목, 첫 글자만 이탤릭(Festivals & Awards · Life's a Trip)
  · 사진 위 작은 고정폭 머리 줄(왼쪽 출처 · 가운데 동그라미 기호 ⓒⓗⓔ · 오른쪽 분류), 사진 아래 '1 / 5   00:00:34'
  · 사진 모서리의 작은 ㄱ자 표시 + 가운데 십자 (필름 프레임)
  · 가운데 정렬 목록: 고정폭 머리 → 굵은 따옴표 이름 → 고정폭 설명, 무리 사이 동그라미 기호 줄
  · 제목을 사진 양쪽으로 나눠 사진을 가로지르게(Life's a Trip | 사진 | Trippie Redd)
  A  필름 카드   — 오른쪽 큰 사진 카드(머리 줄 · 모서리 표시 · 타임코드) + 작은 카드 셋, 왼쪽 글 단
  B  목록         — 왼쪽 사진(큰 사진이 위 · 왼쪽 재단까지) + 작은 셋, 오른쪽 가운데 정렬 목록(Festivals & Awards 꼴)
  C  나뉜 제목    — 가운데 사진을 'What made' | 사진 | 'me stop.' 이 양쪽에서 잡고, 아래 띠에 작은 사진 · 서술 · 맺음
빨간 의자 비율은 이 판에서 잰 0.59%(B20 과 같음). 2-2 세션 글의 0.4% 와 다르다 — 기준을 정하면 바꾼다.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b20 as b20  # noqa: E402

b18 = b20.b18
pe, b10, b17 = b18.pe, b18.b10, b18.b17
raw_t, raw_div = b18.raw_t, b18.raw_div
af = pe.af
OUT, TMP, PRINT = b18.OUT, b18.TMP, b18.PRINT
W, H = b18.W, b18.H

# ── 글 (rev4) ─────────────────────────────────────────────────────────────────────────
FIRST = '넓은 장면에서도 내 눈은 한 점에 먼저 간다.'
Q = '나를 멈추게 하는 것은 무엇일까?'
ANS = '포인트다. 주변과 어울리면서도, 한 가지가 다른 것.'
ANS_EN = 'What stops me is a point — something that belongs to the scene, yet stands apart.'
ROWS = [('a)', '빨간 의자', '바닷가의 의자', '색 하나', 'PH-05'), ('b)', '분홍 수영복', '물놀이하는 사람들', '색 하나', 'PH-01'),
        ('c)', '빨간 신호', '밤거리의 불빛', '빛 하나', 'PH-08'), ('d)', '초록 싹', '마른 잎 사이의 식물', '살아 있는 하나', 'PH-10')]
MEASURE = '빨간 의자는 화면의 0.59%다. 작아도, 어울리는 자리에서 하나만 다르면 눈은 그곳에 먼저 간다.'
DESC = ['나를 멈추게 하는 것은 포인트다. 포인트는 주변과 어울려 한 장면을 이루면서도, 한 가지가 달라 시선을 끈다. 어울리면서 구분되는 것, 그것이 나를 멈추게 한다.',
        '옷을 입을 때도 나는 같은 순서를 따른다. 먼저 색과 원단, 길이를 맞춰 전체를 하나로 만들고, 그다음 한 가지만 다르게 둔다. 그것은 색 하나일 때도, 소재나 핏 하나일 때도 있다.',
        '모두 튀면 어색하고, 모두 맞추기만 하면 눈에 띄지 않는다. 평소 이렇게 입고 다니는 모습을 보고, 지인이 스타일링을 부탁한 적도 있다.']
END = ['진열도 같다. 먼저 전체를 하나로 맞추고,', '그 안에 하나를 구분되게 둔다.']
END_EN = 'A display works the same way: first make the whole agree, then set one thing apart within it.'
TITLE = "<i>W</i>hat made <i>m</i>e stop."


# ── 부품 ──────────────────────────────────────────────────────────────────────────────
def ph(pid, x, y, w, h, **kw):
    b18.STATE[0] += 1
    try:
        return pe.photo(pid, x, y, w, h, **kw)
    finally:
        b18.STATE[0] -= 1


MARKS = {  # 사진 속 포인트 초점 칸 (원본 px)
    'PH-05': lambda to, s: af(*to(1072, 578), 6.5),
    'PH-01': lambda to, s: af(*to(687, 545), 4),
    'PH-08': lambda to, s: af(*to(880, 94), 3.4),
    'PH-10': lambda to, s: af(*to(690, 290), 4.2),
}
SMALL = {'PH-01': dict(focus=(0.458, 0.64), zoom=3.0), 'PH-08': dict(focus=(0.6, 0.2), zoom=1.6), 'PH-10': dict(focus=(0.46, 0.4), zoom=1.4),
         'PH-05': dict(focus=(0.5, 0.5))}


def film(x, y, w, h, r=2.6, inset=1.6):
    """사진 모서리의 작은 ㄱ자 + 가운데 십자 (참고 사이트의 필름 프레임)."""
    a, b, c, d = x + inset, y + inset, x + w - inset, y + h - inset
    cs = ''.join(f"<polyline points='{p}' class='fm'/>" for p in (f'{a + r},{b} {a},{b} {a},{b + r}', f'{c - r},{b} {c},{b} {c},{b + r}',
                                                                  f'{a + r},{d} {a},{d} {a},{d - r}', f'{c - r},{d} {c},{d} {c},{d - r}'))
    mx, my = x + w / 2, y + h / 2
    cs += f"<line x1='{mx - 1.6}' y1='{my}' x2='{mx + 1.6}' y2='{my}' class='fm'/><line x1='{mx}' y1='{my - 1.6}' x2='{mx}' y2='{my + 1.6}' class='fm'/>"
    return raw_div(0, 0, W, H, f"<svg class='ov' viewBox='0 0 {W} {H}'>{cs}</svg>", '')


def circles(active=None):
    return ''.join(f"<span class='cc{' on' if k == active else ''}'>{k}</span>" for k in 'abcd')


def card(pid, x, y, w, h, left, right, active, foot_l='', foot_r=''):
    mid = f"<span class='m'>{circles(active)}</span>" if w > 90 else ''
    if w <= 90:  # 좁은 카드 — 가운데 기호 줄 대신 오른쪽에 제 기호 하나
        right = f"{right}&nbsp;&nbsp;<span class='cc on'>{active}</span>" if right else f"<span class='cc on'>{active}</span>"
    o = [raw_t(x, y - 5.2, w, 4, f"<span class='l'>{left}</span>{mid}<span class='r'>{right}</span>", 'hrow'),
         ph(pid, x, y, w, h, marks=MARKS[pid], **SMALL[pid]), film(x, y, w, h)]
    if foot_l or foot_r:
        o.append(raw_t(x, y + h + 1.6, w, 4, f"<span class='l'>{foot_l}</span><span class='r'>{foot_r}</span>", 'hrow'))
    return ''.join(o)


def p(lines):
    return ''.join(f'<p>{s}</p>' for s in lines)


# ── A · 필름 카드 ──────────────────────────────────────────────────────────────────────
def opt_a():
    X, Wd = 14, 96
    rows = ''.join(f"<div class='r3'><span class='n'>{a}</span><b>{pt}</b><span class='s'>{fit} — {dif}</span></div>" for a, pt, fit, dif, _ in ROWS)
    o = [raw_t(X, 19, Wd, 4, 'PART 1 OBSERVE&nbsp;&nbsp;/&nbsp;&nbsp;06', 'mono'),
         raw_t(X, 25, Wd + 20, 26, TITLE, 'jt'),
         raw_t(X, 44, Wd, 6, FIRST, 'kb6'),
         raw_t(X, 54, Wd, 7, Q, 'q6'),
         raw_t(X, 63, Wd, 7, ANS, 'ans'),
         raw_t(X, 71, Wd - 6, 8, ANS_EN, 'en6 wrap'),
         raw_t(X, 82, Wd, 30, rows, 'rows3'),
         raw_t(X, 116, Wd, 40, ''.join(f'<p>{s}</p>' for s in DESC), 'desc wrap'),
         raw_t(X, 156, Wd, 10, p(END), 'end6'),
         raw_t(X, 167, Wd, 6, END_EN, 'en6 wrap')]
    x0, w0 = 122, 179
    o.append(card('PH-05', x0, 24, w0, 92, 'a)&nbsp;&nbsp;PH-05', '포인트 — 빨간 의자', 'a', '1 / 4', '0.59% OF THE FRAME'))
    o.append(raw_t(x0, 122.5, w0, 12, "<i>A</i> red chair.", 'jt2 c'))
    o.append(raw_t(x0 + 30, 134, w0 - 60, 6, MEASURE, 'cap6 c wrap'))
    cw = (w0 - 2 * 6) / 3
    for i, (a, pt, fit, dif, pid) in enumerate(ROWS[1:]):
        x = x0 + i * (cw + 6)
        o.append(card(pid, x, 150, cw, 22, f'{a}&nbsp;&nbsp;{pt}', dif, a[0], f'{i + 2} / 4', ''))
    return ''.join(o)


# ── B · 목록 (Festivals & Awards) ────────────────────────────────────────────────────
def opt_b():
    o = [ph('PH-05', -3, -3, 158, 114, marks=MARKS['PH-05'], focus=(0.62, 0.5)), film(0, 0, 155, 111),
         raw_div(0, 0, 155, 111, '', 'fadeB'),
         raw_t(14, 6, 120, 4, '<span class=l>a)&nbsp;&nbsp;PH-05</span>', 'hrow lt'),
         raw_t(14, 98, 130, 4, f"<span class='l'>1 / 4</span><span class='r'>0.59% OF THE FRAME</span>", 'hrow lt')]
    cw = (141 - 2 * 4) / 3
    for i, (a, pt, fit, dif, pid) in enumerate(ROWS[1:]):
        x = 14 + i * (cw + 4)
        o.append(card(pid, x, 121, cw, 24, f'{a}&nbsp;&nbsp;{pt}', '', a[0]))
    o.append(raw_t(14, 150, 64, 30, ''.join(f'<p>{s}</p>' for s in DESC[1:]), 'desc s wrap'))
    o.append(raw_t(84, 150, 62, 30, p(END) + f"<p class='e'>{END_EN}</p>", 'end6 s wrap'))
    # 오른쪽 가운데 정렬 목록
    X, Wd = 166, 135
    groups = ''
    for k, (a, pt, fit, dif, _) in enumerate(ROWS):
        if k:
            groups += f"<div class='gl'>{circles()}</div>"
        groups += f"<div class='g'><p class='gh'>{a}&nbsp;&nbsp;{fit}</p><p class='gn'>“{pt}”</p><p class='gd'>{dif}</p></div>"
    o += [raw_t(X, 19, Wd, 14, TITLE, 'jt c'),
          raw_t(X, 37, Wd, 6, FIRST, 'kb6 c'),
          raw_t(X, 47, Wd, 7, Q, 'q6 c'),
          raw_t(X, 56, Wd, 7, ANS, 'ans c'),
          raw_t(X + 10, 64, Wd - 20, 8, ANS_EN, 'en6 c wrap'),
          raw_t(X, 79, Wd, 70, groups, 'awards c'),
          raw_t(X + 6, 161, Wd - 12, 16, DESC[0], 'desc c wrap')]
    return ''.join(o)


# ── C · 나뉜 제목 ──────────────────────────────────────────────────────────────────────
def opt_c():
    px, pw, py, phh = 86, 143, 26, 96
    o = [raw_t(14, 18.5, W - 28, 4, f"<span class='l'>WHAT MADE ME STOP</span><span class='m'>{circles('a')}</span><span class='r'>POINT&nbsp;&nbsp;·&nbsp;&nbsp;0.59%</span>", 'hrow'),
         ph('PH-05', px, py, pw, phh, marks=MARKS['PH-05'], focus=(0.6, 0.5)), film(px, py, pw, phh),
         raw_t(px, py + phh + 1.6, pw, 4, "<span class='l'>a)&nbsp;&nbsp;PH-05&nbsp;&nbsp;빨간 의자</span><span class='r'>1 / 4</span>", 'hrow'),
         raw_t(14, 98, px - 17, 20, '<i>W</i>hat made', 'jt big r'),
         raw_t(px + pw + 3, 98, W - 14 - px - pw - 3, 20, '<i>m</i>e stop.', 'jt big'),
         raw_t(14, 28, px - 20, 6, FIRST, 'kb6 wrap'),
         raw_t(14, 42, px - 20, 7, Q, 'q6 wrap'),
         raw_t(14, 52, px - 20, 14, ANS, 'ans wrap'),
         raw_t(14, 70, px - 22, 10, ANS_EN, 'en6 wrap')]
    groups = ''.join(f"<div class='g'><p class='gh'>{a}&nbsp;&nbsp;{fit}</p><p class='gn'>“{pt}”</p><p class='gd'>{dif}</p></div>" for a, pt, fit, dif, _ in ROWS)
    o.append(raw_t(px + pw + 6, 26, W - 14 - px - pw - 6, 70, groups, 'awards'))
    cw = (112 - 2 * 4) / 3
    for i, (a, pt, fit, dif, pid) in enumerate(ROWS[1:]):
        x = 14 + i * (cw + 4)
        o.append(card(pid, x, 141, cw, 26, f'{a}&nbsp;&nbsp;{pt}', '', a[0]))
    o.append(raw_t(14, 125.5, 112, 6, MEASURE, 'cap6 wrap'))
    o.append(raw_t(134, 129, 98, 48, ''.join(f'<p>{s}</p>' for s in DESC), 'desc s wrap'))
    o.append(raw_t(240, 129, 61, 48, p(END) + f"<p class='e'>{END_EN}</p>", 'end6 s wrap'))
    return ''.join(o)


OPTIONS = [('A', opt_a, '필름 카드'), ('B', opt_b, '목록 · Festivals & Awards'), ('C', opt_c, '나뉜 제목')]

KO = b20.KO
CR = "#EFE3CB"
CSS = b20.CSS + f"""
@font-face{{font-family:Crimson;src:url('file://{pe.FONTS}/CrimsonPro-Regular.ttf')}}
@font-face{{font-family:Crimson;font-style:italic;src:url('file://{pe.FONTS}/CrimsonPro-Italic.ttf')}}
.mono{{font-family:Mono,monospace;font-size:6.4pt;letter-spacing:.12em;color:#9A8F82;white-space:nowrap}}
.jt{{font-family:Crimson,serif;font-size:34pt;line-height:36pt;color:{CR};white-space:nowrap;letter-spacing:-.01em;transform:scaleX(.88);transform-origin:0 0}}
.jt.c{{transform-origin:50% 0}}.jt.big{{font-size:44pt;line-height:46pt}}.jt.big.r{{transform-origin:100% 0}}
.jt i,.jt2 i{{font-style:italic}}
.jt2{{font-family:Crimson,serif;font-size:22pt;line-height:24pt;color:{CR};white-space:nowrap}}
.kb6{{font-family:{KO};font-size:10pt;line-height:15pt;color:#CFC6B8;word-break:keep-all}}.kb6 p{{white-space:normal}}
.q6{{word-break:keep-all;font-family:{KO};font-weight:700;font-size:12.5pt;line-height:17pt;color:{CR};-webkit-text-stroke:.3pt {CR}}}
.ans{{font-family:{KO};font-size:11pt;line-height:16pt;color:#D9773A;word-break:keep-all}}.ans p,.q6 p{{white-space:normal}}
.en6{{font-family:Lora,serif;font-style:italic;font-size:7.6pt;line-height:11pt;color:#8E857A}}.en6 p{{white-space:normal}}
.rows3 .r3{{position:static;display:flex;align-items:baseline;gap:2.4mm;padding:1.3mm 0;border-top:.15mm solid #3a332c}}
.rows3 .r3:last-child{{border-bottom:.15mm solid #3a332c}}
.rows3 .n{{font-family:Mono,monospace;font-size:7pt;color:#D9773A;width:6mm;flex:none}}
.rows3 b{{font-family:{KO};font-weight:700;font-size:9.4pt;color:{CR};width:22mm;flex:none}}
.rows3 .s{{font-family:{KO};font-size:8.4pt;color:#A99F92;white-space:nowrap}}
.desc{{font-family:{KO};font-size:8pt;line-height:13pt;color:#9A8F82;word-break:keep-all}}.desc p{{white-space:normal;margin-bottom:1.6mm}}
.desc.s{{font-size:7.3pt;line-height:11.2pt}}
.end6{{font-family:{KO};font-size:9.6pt;line-height:15pt;color:{CR}}}.end6 p{{white-space:normal}}
.end6.s{{font-size:8.6pt;line-height:13.5pt}}.end6 .e{{font-family:Lora,serif;font-style:italic;font-size:7pt;line-height:10pt;color:#8E857A;margin-top:2mm}}
.cap6{{word-break:keep-all;font-family:{KO};font-size:7.6pt;line-height:11pt;color:#A99F92}}.cap6 p{{white-space:normal}}
.hrow{{font-family:Mono,monospace;font-size:5.6pt;letter-spacing:.08em;color:#9A8F82;white-space:nowrap}}
.hrow>span{{position:absolute;top:0}}.hrow>.l{{left:0}}.hrow>.r{{right:0}}.hrow>.m{{left:50%;transform:translateX(-50%);top:-.3mm}}
.hrow.lt{{color:{CR}}}
.cc{{display:inline-block;width:3.2mm;height:3.2mm;line-height:3mm;margin:0 .5mm;border:.15mm solid #8E857A;border-radius:50%;text-align:center;font-size:4.6pt;color:#8E857A}}
.cc.on{{border-color:#D9773A;color:#D9773A}}
.ov .fm{{fill:none;stroke:rgba(239,227,203,.75);stroke-width:.22}}
.awards .g{{position:static;margin:0 0 1.2mm}}.awards p{{white-space:nowrap}}
.awards .gh{{font-family:{KO};font-size:7.2pt;letter-spacing:.06em;color:#A99F92}}
.awards .gn{{font-family:{KO};font-weight:700;font-size:10pt;line-height:14pt;color:{CR}}}
.awards .gd{{font-family:Mono,monospace;font-size:6.4pt;letter-spacing:.1em;color:#D9773A}}
.awards .gl{{position:static;margin:1.6mm 0 2.6mm}}
.fadeB{{background:linear-gradient(to right,rgba(21,18,15,0) 70%,rgba(21,18,15,1)),linear-gradient(to bottom,rgba(21,18,15,.35),rgba(21,18,15,0) 25%,rgba(21,18,15,0) 70%,rgba(21,18,15,.7))}}
.tagopt{{font-family:Mono,monospace;font-size:5.6pt;letter-spacing:.1em;color:#D9773A;white-space:nowrap}}
"""


def page(fn):
    html, g = b10.page(4, fn, 'g1')
    html = b18.fix_folios(b17.renumber(html)) + b18.grid(False, False)
    return html, g


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for tag, fn, name in OPTIONS:
        html, g = page(fn)
        html += raw_t(220, 5, 81, 4, f'6쪽 · 안 {tag} · {name}', 'tagopt r')
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    h = os.path.join(TMP, 'p06_options.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU p06 options</title><style>{CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'p06_options.pdf'), os.path.join(TMP, 'p06opt')], check=True)


if __name__ == '__main__':
    main()
