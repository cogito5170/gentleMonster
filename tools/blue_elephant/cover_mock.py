"""블루엘리펀트 포트폴리오 표지(PROTEAN) — 오른쪽 아래 버튼 글 + 디자인 요소 안. 사용자가 만든 표지 화면(1870 × 1036) 위에 얹은 시안.

  python3 tools/blue_elephant/cover_mock.py   ->  docs/blue_elephant_portfolio/cover/cover_mock.pdf (2쪽: A 버튼 · B 디자인 요소)

사용자: "포트폴리오 커버를 제작 중이다. 제목은 PROTEAN 으로 설정했다. 우측 하단 버튼에 사용자를 설명할 수 있는 영단어를 넣어라.
또한, 현재의 틀을 바탕으로 '디자인적' 요소를 추가할 수 있다면 추가한 안도 제안해라."
버튼 글: SPACE · LENS · STYLE — 건축 · 사진(+ 안경 렌즈) · 패션. 공고 우대 '패션 · 사진 · 건축'(04_analysis D 유형)과 사용자 소개 'DESIGNER'.
  가운데 버튼의 '2026' 은 오른쪽 위 '2026' 과 겹쳐 글로 바꾼다. 원래 테두리만 있던 버튼 둘은 아래 글자를 가리려고 어두운 반투명 채움으로.
B 안 디자인 요소(블루엘리펀트 화면 말 — 원 · 렌즈, 번호 시리즈 카드, 'Familiar Unfamiliar'):
  ① 사전 뜻풀이 한 줄 — pro·te·an: 모양을 자유롭게 바꾸는 (제목의 뜻을 표지에서 바로 읽게)
  ② 제목의 O 를 렌즈처럼 감싸는 가는 원 하나 — 안경 · 렌즈 · 원(블루엘리펀트의 원형 진열 · 구)
  ③ 버튼에 번호 01 · 02 · 03 — 인스타그램 번호 시리즈 카드의 꼴
  ④ 맨 위 가는 기준선 + 눈금, 네 모서리 뷰파인더 표시, 오른쪽 렌즈에 초점 괄호와 'LENS — 02' 꼬리표
  ⑤ 세로 글 'FAMILIAR UNFAMILIAR' (블루엘리펀트 키워드, 공식 문구 C9)
그림은 그리지 않는다 — 글 · 선 · 원 같은 레이아웃 요소만 얹는다.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
FONTS = os.path.join(REPO, 'tools/p1_layout/fonts')
DIR = os.path.join(REPO, 'docs/blue_elephant_portfolio/cover')
TMP = os.path.join(REPO, 'out/blue_elephant')
PRINT = os.path.join(REPO, 'tools/p1_layout/print_pdf.mjs')
BGI = os.path.join(DIR, 'cover_in_progress.jpg')
W, H = 1870, 1036
CREAM, INK = '#F3D77F', '#1B140C'
PILLS = [(1235, 1426), (1441, 1632), (1648, 1839)]   # 사용자 화면에서 잰 버튼 x (y 967–1015)
WORDS = ['SPACE', 'LENS', 'STYLE']


def box(x, y, w, h, inner='', cls='', style=''):
    return f"<div class='{cls}' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}'>{inner}</div>"


def pills(numbered=False):
    o = ''
    for i, ((x0, x1), w) in enumerate(zip(PILLS, WORDS)):
        label = f"<span class='n'>0{i + 1}</span>{w}" if numbered else w
        o += box(x0, 967, x1 - x0, 48, f'<p>{label}</p>', 'pill' + (' on' if i == 0 else ''))
    return o


def design():
    vf = ''
    for (x, y, dx, dy) in [(14, 14, 1, 1), (W - 14, 14, -1, 1), (14, H - 10, 1, -1), (W - 14, H - 10, -1, -1)]:
        vf += f"<polyline points='{x + dx * 34},{y} {x},{y} {x},{y + dy * 34}'/>"
    ticks = ''.join(f"<line x1='{x}' y1='96' x2='{x}' y2='{102 if (x - 56) % 220 else 108}'/>" for x in range(56, 1816, 44))
    lens = ''.join(f"<polyline points='{p}'/>" for p in ('820,190 800,190 800,210', '1010,190 1030,190 1030,210',
                                                         '820,380 800,380 800,360', '1010,380 1030,380 1030,360'))
    svg = (f"<svg class='ov' viewBox='0 0 {W} {H}'><g class='ln'>{vf}<line x1='56' y1='96' x2='1816' y2='96'/>{ticks}{lens}"
           f"<line x1='1030' y1='285' x2='1090' y2='285'/></g>"
           f"<circle cx='762' cy='827' r='138' class='ring'/></svg>")
    return (svg
            + box(1096, 274, 200, 24, '<p>LENS — 02</p>', 'tag')
            + box(186, 652, 900, 40, "<p><b>pro·te·an</b>&nbsp;&nbsp;[ˈprō-tē-ən]&nbsp;&nbsp;<i>adj.</i>&nbsp;&nbsp;able to take many forms — space, lens, style.</p>", 'dict')
            + box(1806, 420, 30, 420, '<p>FAMILIAR UNFAMILIAR</p>', 'vert')
            + box(56, 935, 120, 22, '<p>No. 00 / COVER</p>', 'tag'))


CSS = f"""
@font-face{{font-family:Inst;font-weight:700;src:url('file://{FONTS}/InstrumentSans-Bold.ttf')}}
@font-face{{font-family:Inst;font-weight:400;src:url('file://{FONTS}/InstrumentSans-Regular.ttf')}}
@font-face{{font-family:Mono;src:url('file://{FONTS}/IBMPlexMono-Regular.ttf')}}
@font-face{{font-family:Lora;font-style:italic;src:url('file://{FONTS}/Lora-Italic.ttf')}}
@page{{size:{W}px {H}px;margin:0}}*{{margin:0;padding:0}}
.sheet{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:url('file://{BGI}') 0 0/{W}px {H}px;page-break-after:always}}
.sheet div,.sheet svg{{position:absolute}}.ov{{left:0;top:0;width:{W}px;height:{H}px}}
.pill{{box-sizing:border-box;border:2px solid #fff;border-radius:24px;background:rgba(27,20,12,.82);display:flex;align-items:center;justify-content:center}}
.pill p{{font-family:Inst,sans-serif;font-weight:700;font-size:21px;letter-spacing:.12em;color:#fff;white-space:nowrap}}
.pill.on{{background:#fff}}.pill.on p{{color:{INK}}}
.pill .n{{font-family:Mono,monospace;font-weight:400;font-size:13px;letter-spacing:.04em;margin-right:10px;opacity:.75}}
.ln{{fill:none;stroke:#fff;stroke-width:2;stroke-opacity:.85}}
.ring{{fill:none;stroke:{CREAM};stroke-width:3}}
.tag{{font-family:Mono,monospace;font-size:14px;letter-spacing:.08em;color:#fff;white-space:nowrap}}
.dict{{font-family:Mono,monospace;font-size:17px;color:#fff;white-space:nowrap;letter-spacing:.02em}}.dict b{{font-family:Inst,sans-serif;font-size:20px}}
.dict i{{font-family:Lora,serif}}
.vert p{{font-family:Mono,monospace;font-size:14px;letter-spacing:.32em;color:#fff;white-space:nowrap;transform:rotate(90deg);transform-origin:0 0;position:absolute;left:24px;top:0}}
.label{{font-family:Mono,monospace;font-size:15px;color:#fff;background:rgba(0,0,0,.55);padding:4px 10px}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    pages = [pills() + box(760, 18, 360, 26, '<p>시안 A — 버튼 글</p>', 'label'),
             design() + pills(True) + box(760, 18, 360, 26, '<p>시안 B — 디자인 요소</p>', 'label')]
    h = os.path.join(TMP, 'cover_mock.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=en><head><meta charset=utf-8><title>PROTEAN cover mock</title><style>{CSS}</style></head><body>"
                + ''.join(f"<div class='sheet'>{p}</div>" for p in pages) + '</body></html>')
    subprocess.run(['node', PRINT, h, os.path.join(DIR, 'cover_mock.pdf'), os.path.join(TMP, 'cover_mock')], check=True)


if __name__ == '__main__':
    main()
