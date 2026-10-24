"""JAJU 포트폴리오 8쪽 /02 Match. 파트 표지 — 사용자가 만든 표지 이미지 위에 얹을 글 (315 × 195).

  python3 tools/jaju_layout/cover_match.py   ->  docs/jaju_rounding_vmd/layout/cover_match.pdf  (1쪽: 자리 표시 위 미리 보기)
                                             ->  out/jaju_layout/cover_match_text.html    (글만 — InDesign 용)

사용자: "첫번째 이미지는 Match 에 대한 커버 페이지 사례(POLITICS + PARTNERSHIPS, bookcoverarchive)이다. 두번째 이미지는 현재 제작 중인
커버 페이지이다. 제작 중인 이미지 위에 사례를 참고하여 스토리에 적합한 텍스트를 첨가하라."
사례에서 가져온 것:
  · 글은 모두 왼쪽 색 면(빨강 → 여기서는 파란 벽) 안에만. 오른쪽 흰 벽 · 바닥 · 인물에는 글을 올리지 않는다
  · 위: 작은 굵은 대문자 'EDITED BY' / 좁은 굵은 이름 / 'AND' / 이름 — 작은 줄과 큰 줄이 번갈아 넷
  · 가운데 아래: 흰색 좁은 굵은 제목 두 줄, 두 낱말을 검정 '+' 로 잇는다 (POLITICS + PARTNERSHIPS)
  · 그 아래: 검정 작은 대문자 부제 네 줄, 넓은 자간 · 넉넉한 줄 간격. 바닥 사선(파란 바닥)보다 위에서 끝난다
글(2-2 세션 파트 2 '맞추다' 확정 스토리): 표지 한국어 '사람을 멈추게 한 조화를, 내 옷으로 맞춰 본다.'
  영어 'Matching my own clothes, to find the harmony that makes people stop.'
  제목 'CLOTHES + PLACE' — 파트 2 의 끝 문장 '옷은 놓인 장소와 맞을 때 완성된다.'를 사례의 '+' 꼴로. 그림(색 방 안의 한 벌)과 같은 말.
자리 표시: 사용자 이미지(1820 × 1130 화면 캡처)에서 잰 비율 — 파란 벽 x 0–33.2% · 바닥선 y 76.5% · 사선 (33.2%, 76.5%) → (1.1%, 100%),
  인물 x 68.7–84.1% · y 13.1–79%. 미리 보기에서만 그리고 InDesign 파일에는 넣지 않는다(사용자 이미지를 맨 아래에 놓아 쓴다).
좁은 굵은 글꼴이 이 환경에 없어 Instrument Sans Bold 를 장평 74% 로 썼다 — InDesign 에서 가진 좁은 고딕(예: 210 타임라인 Bold)으로 바꿔도 자리는 같다.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
FONTS = os.path.join(REPO, 'tools/p1_layout/fonts')
OUT = os.path.join(REPO, 'docs/jaju_rounding_vmd/layout')
TMP = os.path.join(REPO, 'out/jaju_layout')
PRINT = os.path.join(REPO, 'tools/p1_layout/print_pdf.mjs')
W, H = 315, 195

WALL_X, FLOOR_Y, DIAG_X = 0.332 * W, 0.765 * H, 0.011 * W   # 사용자 이미지에서 잰 자리
FIG = (0.687 * W, 0.131 * H, 0.154 * W, 0.659 * H)
L = 14                                                     # 왼쪽 여백 (책의 다른 쪽과 같음)

TOP = [('PART 2', 'sm'), ('/02 MATCH.', 'nm'), ('OF', 'sm'), ('FROM THE INSIDE', 'nm')]
TITLE = ['CLOTHES', 'PLACE']
PLUS_X = 82.6                                             # CLOTHES 끝(79.3) + 낱말 사이 — '+' 는 따로 한 상자 (InDesign 에서 옮기기 쉽게)
SUB = ['MATCHING MY OWN CLOTHES,', 'TO FIND THE HARMONY', 'THAT MAKES', 'PEOPLE STOP.']
KO_LINES = ['사람을 멈추게 한 조화를,', '내 옷으로 맞춰 본다.']


def d(x, y, w, h, inner, cls, attrs=''):
    return f"<div class='{cls}' {attrs} style='left:{x:.2f}mm;top:{y:.2f}mm;width:{w:.2f}mm;height:{h:.2f}mm'>{inner}</div>"


def text():
    o = []
    y = 14
    for s, c in TOP:  # 작은 줄 · 큰 줄 번갈아 (EDITED BY / 이름 / AND / 이름)
        o.append(d(L, y, 88, 9, f'<p>{s}</p>', 't ' + c))
        y += 4.6 if c == 'sm' else 9.4
    o.append(d(L, 96, 92, 40, ''.join(f'<p>{s}</p>' for s in TITLE), 't ttl'))
    o.append(d(PLUS_X, 96, 14, 20, '<p>+</p>', 't ttl pl'))
    o.append(d(L, 136, 80, 22, ''.join(f'<p>{s}</p>' for s in SUB), 't sub'))
    o.append(d(L, 160.5, 70, 12, ''.join(f'<p>{s}</p>' for s in KO_LINES), 't ko'))
    return ''.join(o)


def guides():
    """사용자 이미지 자리 표시 — 미리 보기 전용."""
    fx, fy, fw, fh = FIG
    return (f"<svg class='gd' viewBox='0 0 {W} {H}'>"
            f"<rect x='0' y='0' width='{W}' height='{H}' fill='#FFFFFF'/>"
            f"<polygon points='0,{FLOOR_Y} {W},{FLOOR_Y} {W},{H} {DIAG_X},{H}' fill='#E2AA88'/>"
            f"<polygon points='0,0 {WALL_X},0 {WALL_X},{FLOOR_Y} {DIAG_X},{H} 0,{H}' fill='#86A7D0'/>"
            f"<rect x='{fx}' y='{fy}' width='{fw}' height='{fh}' fill='none' stroke='#9A8F82' stroke-width='.3' stroke-dasharray='1.4 1'/>"
            f"<text x='{fx + fw / 2}' y='{fy + fh / 2}' text-anchor='middle' class='gt'>인물 (사용자 이미지)</text>"
            f"<text x='{W - 4}' y='{H - 4}' text-anchor='end' class='gt'>자리 표시 — 실제 표지 이미지로 바꿈</text></svg>")


CSS = f"""
@font-face{{font-family:Inst;font-weight:400;src:url('file://{FONTS}/InstrumentSans-Regular.ttf')}}
@font-face{{font-family:Inst;font-weight:700;src:url('file://{FONTS}/InstrumentSans-Bold.ttf')}}
@page{{size:{W}mm {H}mm;margin:0}}*{{margin:0;padding:0}}
.sheet{{position:relative;width:{W}mm;height:{H}mm;overflow:hidden;page-break-after:always}}
.sheet div,.sheet svg{{position:absolute}}.gd{{left:0;top:0;width:{W}mm;height:{H}mm}}
.gt{{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:2.6px;fill:#7a736b}}
.t p{{white-space:nowrap}}
.sm{{font-family:Inst,sans-serif;font-weight:700;font-size:7.6pt;line-height:10pt;letter-spacing:.09em;color:#1B1B1A}}
.nm{{font-family:Inst,sans-serif;font-weight:700;font-size:22pt;line-height:24pt;letter-spacing:.01em;color:#1B1B1A;transform:scaleX(.74);transform-origin:0 0}}
.ttl{{font-family:Inst,sans-serif;font-weight:700;font-size:54pt;line-height:50pt;letter-spacing:-.005em;color:#FFFFFF;transform:scaleX(.74);transform-origin:0 0}}
.ttl.pl{{color:#1B1B1A}}
.sub{{font-family:Inst,sans-serif;font-weight:700;font-size:7.6pt;line-height:13.2pt;letter-spacing:.1em;color:#1B1B1A}}
.ko{{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:9.4pt;line-height:14pt;color:#1B1B1A;-webkit-text-stroke:.15pt #1B1B1A}}
"""


def write(name, body, bg):
    h = os.path.join(TMP, name + '.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU /02 Match cover</title><style>{CSS}</style></head>"
                f"<body><div class='sheet' style='background:{bg}'>{body}</div></body></html>")
    return h


def main():
    os.makedirs(TMP, exist_ok=True)
    h = write('cover_match', guides() + text(), '#FFFFFF')
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'cover_match.pdf'), os.path.join(TMP, 'cover_match')], check=True)
    write('cover_match_text', text().replace("class='t ko'", "data-font='210 타임라인|Regular' class='t ko'"), 'transparent')


if __name__ == '__main__':
    main()
