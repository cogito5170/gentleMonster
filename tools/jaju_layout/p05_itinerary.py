"""JAJU 포트폴리오 5쪽 Where people stop? — 일정표(ITINERARY) 격자 꼴 (315 × 195, B20 의 기준선 · 십자 · 바닥 줄).

  python3 tools/jaju_layout/p05_itinerary.py   ->  docs/jaju_rounding_vmd/layout/p05_itinerary.pdf

사용자: "해당 사례(HOUSE OF ALIGNMENT · ITINERARY 4 × 4 격자)를 참고하여 5페이지의 스타일을 변형하여라. 비례, 텍스트 등의 요소는 포트폴리오 사례를 참고한다."
참고에서 가져온 것:
  · 가는 선의 같은 크기 칸 격자, 바깥 테두리까지 — 사진은 칸을 꽉 채우고 칸끼리 붙지 않게 엇갈려(대각선) 놓는다
  · 글 칸: 왼쪽 위에 번호 '(1.1)' + 대문자 머리, 내용은 칸 아래쪽에 붙인다 · 목록은 '7AM → WALK' 꼴의 화살표
  · 빈 칸을 남겨 숨을 둔다 (16칸 중 5칸 → 여기 15칸 중 4칸)
  · 격자 아래 큰 글자 두 덩이 '( ITINERARY )' | '(WWW.) HOUSE OF …' → '( WHERE PEOPLE STOP? )' | '(05) 무엇이 그들을 멈추게 했을까?'
비례: 내용 폭 287 = 5칸 × 57.4, 높이 3줄 × 46 (칸 1.25 : 1 — 참고의 세로 칸을 가로 판형에 맞춤). 사진 원본 16:9 는 점선 틀 가운데로 잘라 넣는다.
글: B19 5쪽(A안 위 · B안 아래)을 칸으로 나눔 — 5.1 본 자리 · 5.2 쉼(01–03) · 5.3 행위(04–06) · 5.4 왜(B안 서술) · 5.5 다음 질문.
사례의 글자 위계(1 ETÉREO · 6 Desjobert): 고정폭 번호 · 머리 6.4pt → 내용 7pt → 큰 글자 15pt 두 덩이.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import p06_options as po  # noqa: E402  (B20 · 격자 · 바닥 줄 · 글꼴)
import plan_b19 as b19  # noqa: E402

b18, b13 = po.b18, b19.b13
raw_t, raw_div, ph = po.raw_t, po.raw_div, po.ph
OUT, TMP, PRINT, W, H = po.OUT, po.TMP, po.PRINT, po.W, po.H
KO, CR = po.KO, po.CR

X0, Y0, COLS, ROWS, CW, RH = 14, 17, 5, 3, 287 / 5, 46
# 칸 배치 — P: 사진(b13.A 의 번호), T: 글 칸, '.': 빈 칸. 사진끼리는 변으로 붙지 않는다.
MAP = [['T1', 'P0', 'T2', 'P1', '.'],
       ['P2', '.', 'P3', 'T3', 'P4'],
       ['.', 'T4', '.', 'P5', 'T5']]

ARROW = "<span class='ar'>→</span>"


def lst(rows):
    return ''.join(f"<p><span class='nn'>{n}</span>{w} {ARROW} {q}</p>" for n, w, q in rows)


REST = [(f'{i + 1:02d}', a[1], a[3]) for i, a in enumerate(b13.A[:3])]
ACT = [(f'{i + 4:02d}', a[1], a[3]) for i, a in enumerate(b13.A[3:])]
TEXT = {  # 번호, 머리, 칸 아래 내용, 칸 class
    'T1': ('(5.1)', 'WHERE THEY STOPPED', ''.join(f'<p>{s}</p>' for s in b19.INTRO), 'cb'),
    'T2': ('(5.2)', '01–03&nbsp;&nbsp;REST · 쉼', f"<p class='k'>{b19.A[0][2]}</p>" + lst(REST), 'cb'),
    'T3': ('(5.3)', '04–06&nbsp;&nbsp;ACT · 행위', f"<p class='k'>{b19.A[1][2]}</p>" + lst(ACT), 'cb'),
    'T4': ('(5.4)', 'WHY', f'<p>{b19.B}</p>', 'cb xs'),
    'T5': ('(5.5)', 'NEXT', ''.join(f'<p>{s}</p>' for s in b19.END), 'cb'),
}


def cell(x, y, w, h, key):
    no, head, body, cls = TEXT[key]
    return (raw_t(x + 2.4, y + 2.2, w - 4.8, 8, f"<p><span class='no'>{no}</span></p><p>{head}</p>", 'ch')
            + raw_t(x + 2.4, y + 10, w - 4.8, h - 12.6, body, cls + ' wrap'))


def photo_cell(x, y, w, h, i):
    pid, place, en, q, box = b13.A[i]
    fx, fy, fw, fh = box
    o = [ph(pid, x, y, w, h, focus=(fx + fw / 2, fy + fh / 2), marks=b13.dashed(pid, box, en)),
         raw_t(x + 2.2, y + 2, 20, 4, f'({i + 1:02d})', 'pno')]
    return ''.join(o)


def lines():
    ln = []
    for c in range(COLS + 1):
        x = X0 + c * CW
        ln.append(f"<line x1='{x:.2f}' y1='{Y0}' x2='{x:.2f}' y2='{Y0 + ROWS * RH}' class='gl'/>")
    for r in range(ROWS + 1):
        y = Y0 + r * RH
        ln.append(f"<line x1='{X0}' y1='{y}' x2='{X0 + COLS * CW:.2f}' y2='{y}' class='gl'/>")
    return raw_div(0, 0, W, H, f"<svg class='ov' viewBox='0 0 {W} {H}'>{''.join(ln)}</svg>", '')


def p05():
    o = []
    for r, row in enumerate(MAP):
        for c, k in enumerate(row):
            x, y = X0 + c * CW, Y0 + r * RH
            if k[0] == 'P':
                o.append(photo_cell(x, y, CW, RH, int(k[1])))
            elif k[0] == 'T':
                o.append(cell(x, y, CW, RH, k))
    o.append(lines())
    yb = Y0 + ROWS * RH
    # 격자 아래 큰 글자 두 덩이 — 왼쪽 칸 1 · 오른쪽은 셋째 칸 선에서 (참고의 (ITINERARY) | (WWW.) …)
    o.append(raw_t(X0, yb + 11, 2 * CW, 9, '( WHERE PEOPLE STOP? )', 'big'))
    o.append(raw_t(X0 + 2 * CW, yb + 4.6, 2 * CW + 4, 16, "<p>(05)</p><p class='k'>무엇이 그들을 멈추게 했을까?</p>", 'big'))
    o.append(raw_t(X0 + 4 * CW + 2.4, yb + 6.2, CW - 2.4, 12, b19.A_EN, 'en5 wrap'))
    return ''.join(o)


def page():
    html, g = b18.b10.page(3, p05, 'g1')  # b15.PAGES 의 3번 = 5쪽
    return b18.fix_folios(b18.b17.renumber(html)) + b18.grid(False, False), g


CSS = po.CSS + f"""
@font-face{{font-family:Inst;src:url('file://{po.pe.FONTS}/InstrumentSans-Regular.ttf')}}
.ov .gl{{stroke:#EFE7DA;stroke-opacity:.32;stroke-width:.2}}
.ch{{font-family:Mono,monospace;font-size:6.4pt;line-height:8.4pt;letter-spacing:.04em;color:{CR};text-transform:uppercase}}
.ch .no{{color:#D9773A}}
.pno{{font-family:Mono,monospace;font-size:6pt;letter-spacing:.04em;color:{CR};text-shadow:0 0 .6mm rgba(0,0,0,.7)}}
.cb{{display:flex;flex-direction:column;justify-content:flex-end;font-family:{KO};font-size:7pt;line-height:11pt;color:{CR};word-break:keep-all}}
.cb p{{white-space:normal}}.cb .k{{font-weight:700;-webkit-text-stroke:.2pt {CR};margin-bottom:1.4mm}}
.cb .nn{{font-family:Mono,monospace;font-size:6.4pt;color:#9A8F82;margin-right:1.6mm}}
.cb .ar{{font-family:Mono,monospace;color:#D9773A}}
.cb.xs{{font-size:6.5pt;line-height:9.9pt;color:#CFC6B8}}
.big{{font-family:Inst,sans-serif;font-size:15pt;line-height:17pt;color:{CR};white-space:nowrap;letter-spacing:-.005em}}
.big .k{{font-family:{KO};font-size:14pt;line-height:18pt}}
.en5{{display:flex;flex-direction:column;justify-content:flex-end;font-family:Lora,serif;font-style:italic;font-size:7pt;line-height:10pt;color:#8E857A}}
.en5 p{{white-space:normal}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    html, g = page()
    h = os.path.join(TMP, 'p05_itinerary.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU p05 itinerary</title><style>{CSS}</style></head>"
                f"<body><div class='sheet {g}'>{html}</div></body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'p05_itinerary.pdf'), os.path.join(TMP, 'p05i')], check=True)


if __name__ == '__main__':
    main()
