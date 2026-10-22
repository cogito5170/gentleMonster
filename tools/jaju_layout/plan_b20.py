"""JAJU 포트폴리오 — B20: B19(315 × 195) 그대로, 6쪽 What made me stop. 을 '여백 — 한 점'으로 바꾼 판.

  python3 tools/jaju_layout/plan_b20.py   ->  docs/jaju_rounding_vmd/layout/plan_b20.pdf (18쪽)

요청: 2-2 세션(스토리, 브랜치 claude/awesome-keller-otac19 d790230 · docs/jaju_rounding_vmd/p06_story.md)이 사용자 지시로 보낸 6쪽 변경안.
  5쪽의 답(01–03 여백 · 04–06 감각)을 6쪽이 "나를 멈추게 한 것도 같았다. 넓게 비어 있는 장면, 그 안의 한 점."으로 받는다.
글자 위계는 사용자가 고친 5쪽과 맞춘다: 제목 19pt → 첫 문장 굵게 → 영어 이탤릭 → 작은 머리글 + 표(주황 기호 + 굵은 낱말 — 한 점) → 맺음.
사진 표시: 큰 사진(PH-05)의 'WIDE' 직사각형 → 점선 '여백 MARGIN', 의자 초점 칸 → '한 점 POINT', 견본 두 칸 + 비율.
견본 · 비율은 이 판에서 다시 잰 값(원본 PH-05, 1125 × 632):
  여백  #537F95 — 사진 높이 35–65% 띠의 평균
  한 점 #7E2123 — 오른쪽 아래(가로 85% · 세로 75% 너머)에서 R > 100 · R > 1.8G · R > 1.8B 인 픽셀 4,177개의 평균 = 화면의 0.59%
  (2-2 세션 값 #61889E · #882528 · 0.4% 와 다르다 — 잰 범위 · 기준이 다르기 때문. 기준을 정하면 그 값으로 바꾼다)
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b19 as b19  # noqa: E402

b18 = b19.b18
pe = b18.pe
photo, af, frame = pe.photo, pe.af, pe.frame
raw_t, raw_div = b18.raw_t, b18.raw_div
SX, SY = b18.SX, b18.SY
OUT, TMP, PRINT = b18.OUT, b18.TMP, b18.PRINT

MARGIN_HEX, POINT_HEX, POINT_PCT = '#537F95', '#7E2123', '0.59%'
ROWS = [('a)', '파란 바다', '빨간 의자'), ('b)', '저녁의 얕은 물', '분홍 수영복'), ('c)', '밤의 어둠', '빨간 신호'), ('d)', '마른 잎', '초록 싹')]


def p_detail():
    W5, H5 = 178 * SX, 100 * SY  # 큰 사진 틀(옮긴 크기)

    def chair(to, s):
        cx, cy = to(1072, 578)
        x0, y0, w, h = 6, 6, W5 - 12, H5 - 26
        r = f"x='{x0}' y='{y0}' width='{w:.2f}' height='{h:.2f}'"
        return (f"<rect {r} class='dshs'/><rect {r} class='dsh'/><text x='{x0 + .6}' y='{y0 - 1.3}' class='afs'>여백 MARGIN</text>"
                + af(cx, cy, 6.5, '한 점 POINT', 'left'))

    def pink(to, s):
        return af(*to(687, 545), 4, 'b)')

    def sig(to, s):
        return af(*to(880, 94), 3.4, 'c)')

    def sprout(to, s):
        return af(*to(690, 290), 4.2, 'd)')

    X, Wd = 14, 88
    rows = ''.join(f"<div class='a5'><span class='n'>{a}</span><b>{w}</b><span class='d'>—</span><span class='s'>{p}</span></div>" for a, w, p in ROWS)
    sw = (f"<span class='lb'>여백</span><i style='background:{MARGIN_HEX}'></i><span class='hx'>{MARGIN_HEX}</span>"
          f"<span class='lb'>한 점</span><i style='background:{POINT_HEX}'></i><span class='hx'>{POINT_HEX}</span>"
          f"<span class='lb'>빨간 의자 = 화면의</span>&nbsp;<span class='hx'>{POINT_PCT}</span>")
    caps = [(109, 'b)', '저녁의 얕은 물', '분홍 수영복'), (169.5, 'c)', '밤의 어둠', '빨간 신호'), (230, 'd)', '마른 잎', '초록 싹')]
    o = [
        raw_t(X, 19.5, Wd + 10, 10, 'What made me stop.', 'h2'),
        raw_t(X, 36, Wd, 14, '<p>나를 멈추게 한 것도 같았다.</p><p>넓게 비어 있는 장면, 그 안의 한 점.</p>', 'q6'),
        raw_t(X, 51, Wd - 4, 10, 'What stopped me was the same — a wide, empty scene, and one point inside it.', 'enb wrap'),
        raw_t(X, 68, Wd, 4, '여백 — 한 점', 'lab6'),
        raw_t(X, 73, Wd, 36, rows, 'arows'),
        raw_t(X, 140, Wd, 20, '<p>진열도 같다.</p><p>다 채우지 않고 여백을 남기고,</p><p>눈이 먼저 닿을 한 점을 그 안에 둔다.</p>', 'end5'),
        raw_t(X, 162, Wd - 4, 12, 'A display works the same way: leave a margin, and place inside it the one point the eye should meet first.', 'enb wrap'),
        raw_t(109 * SX, 14.2, W5, 4, sw, 'sw6'),
        photo('PH-05', 109, 22, 178, 100, focus=(0.5, 0.5), marks=chair),
        photo('PH-01', 109, 128, 57, 50, focus=(0.458, 0.64), zoom=3.0, marks=pink),
        photo('PH-08', 169.5, 128, 57, 50, focus=(0.6, 0.2), zoom=1.6, marks=sig),
        photo('PH-10', 230, 128, 57, 50, focus=(0.46, 0.4), zoom=1.4, marks=sprout),
    ]
    for x, a, w, p in caps:
        o.append(raw_t(x * SX, 178 * SY + 1.6, 57 * SX, 5, f"<p><span class='n3'>{a}</span><b>{w}–</b> {p}</p>", 'cap'))
    o.append(b18.b4.RAW(4, 'PART 1 OBSERVE'))
    return ''.join(o)


b18.OPENERS[4] = p_detail  # b15.PAGES 의 4번 = 6쪽

KO = b19.KO
CSS = b19.CSS + f"""
.q6{{font-family:{KO};font-weight:700;font-size:13pt;line-height:19pt;color:#EFE7DA;white-space:nowrap;-webkit-text-stroke:.3pt #EFE7DA}}
.lab6{{font-family:Mono,monospace;font-size:7pt;letter-spacing:.1em;color:#9A8F82;white-space:nowrap}}
.arows .a5 b{{width:auto;min-width:24mm}}
.sw6{{font-family:Mono,monospace;font-size:6pt;letter-spacing:.06em;color:#9A8F82;white-space:nowrap;text-align:right}}
.sw6 i{{display:inline-block;width:2.4mm;height:2.4mm;vertical-align:-.4mm;margin:0 1.2mm 0 1.6mm}}
.sw6 .lb{{margin-left:4mm;font-family:{KO}}}.sw6 .hx{{color:#EFE7DA}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'plan_b20.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B20</title><style>{CSS}</style></head>"
                f"<body>{''.join(b18.sheets())}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b20.pdf'), os.path.join(TMP, 'plan_b20')], check=True)


if __name__ == '__main__':
    main()
