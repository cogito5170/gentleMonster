"""JAJU 포트폴리오 — B19: B18(315 × 195) 그대로, 5쪽 Where people stop? 왼쪽 단에 '무엇이 그들을 멈추게 했을까?'의 답을 넣은 판.

  python3 tools/jaju_layout/plan_b19.py   ->  docs/jaju_rounding_vmd/layout/plan_b19.pdf (18쪽)

사용자: "A안과 B안 모두 기재한다. A안이 위에서 보여주고, B안이 위에서 서술한다(아래에서). 텍스트 크기 · 레이아웃은 포트폴리오 사례를 참조."
글: docs/jaju_rounding_vmd/p05_why_they_stop.md — A안(짧게 보여 주기) 위, B안(문장으로 서술) 아래.
제목 · 첫 문단은 사용자가 InDesign 에서 고친 5쪽('Where people stop?', '사람들이 멈춘 자리를 본다. …')을 따른다.
글자 크기 · 위계(사례 1 ETÉREO · 6 Desjobert · Galatasaray): 제목 19pt → 질문 13pt 굵게 → 두 줄 표(고정폭 번호 + 굵은 낱말 + 한 줄)
→ 영어 한 줄 이탤릭 → 가는 선 → 서술 한 문단 회색 8.6pt → 맺음 두 줄.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b18 as b18  # noqa: E402

b13, pe = b18.b17.b16.b15.b13, b18.pe
t, photo = pe.t, pe.photo
raw_t, raw_div = b18.raw_t, b18.raw_div
OUT, TMP, PRINT = b18.OUT, b18.TMP, b18.PRINT

INTRO = ['사람들이 멈춘 자리를 본다.', '얕은 물, 파라솔 옆, 가게 계단,', '불판 앞, 간판 앞, 메뉴판 앞.']
A = [('01–03', '쉼', '머물러도 되는 여백이 있었다.'), ('04–06', '행위', '고를 이유가 먼저 보였다.')]
A_EN = 'What made them stop? A margin to rest in, and a signal to choose by.'
B = ('그들을 멈추게 한 것은 상품이 아니라 자리였다. 얕은 물과 그늘, 가게 앞 계단은 잠깐 머물러도 된다고 허락했고, '
     '불판의 연기와 간판의 빛, 메뉴판의 사진은 고를 이유를 먼저 보여 주었다. 사람은 머물 수 있어야 들여다보고, 들여다봐야 고른다.')
END = ['나도 가게 앞에서 질문 하나를 한다.', '어떻게 하면 지나가던 사람들이 멈출까?']


def p_grid():
    gx, gy, cw, ch, gap = 100, 22, 89.5, 46.5, 4  # 사진은 B18 과 같은 자리(옮김)
    X, Wd = 14, 82
    rows = ''.join(f"<div class='a5'><span class='n'>{n}</span><b>{w}</b><span class='d'>—</span><span class='s'>{s}</span></div>" for n, w, s in A)
    o = [
        raw_t(X, 19.5, Wd + 10, 10, 'Where people stop?', 'h2'),
        raw_t(X, 36, Wd, 20, ''.join(f'<p>{s}</p>' for s in INTRO), 'kb5'),
        raw_t(X, 62, Wd, 7, '무엇이 그들을 멈추게 했을까?', 'q5'),
        raw_t(X, 72, Wd, 16, rows, 'arows'),
        raw_t(X, 88, Wd, 10, A_EN, 'enb wrap'),
        raw_div(X, 103, 22, .2, '', 'rule5'),
        raw_t(X, 108, Wd, 40, f'<p>{B}</p>', 'b5 wrap'),
        raw_t(X, 146, Wd, 14, ''.join(f'<p>{s}</p>' for s in END), 'end5'),
    ]
    for i, (pid, place, en, q, box) in enumerate(b13.A):
        r, c = divmod(i, 2)
        x, y = gx + c * (cw + gap), gy + r * (ch + 10)
        hx = pe.accent(pid)
        o.append(photo(pid, x, y, cw, ch, marks=b13.dashed(pid, box, en)))
        o.append(t(x, y + ch + 1.8, cw, 6, f"<p><span class='n3'>N°{i + 1:02d}</span><b>{place}–</b> {q}"
                                           f"<span class='sw3' style='background:{hx}'></span><span class='hx3'>{hx}</span></p>", 'cap'))
    return ''.join(o)


b18.OPENERS[3] = p_grid  # b15.PAGES 의 3번 = 5쪽

KO = "'WenQuanYi Zen Hei',sans-serif"
CSS = b18.CSS + f"""
.kb5{{font-family:{KO};font-size:10pt;line-height:16pt;color:#EFE7DA}}
.q5{{font-family:{KO};font-weight:700;font-size:13pt;line-height:17pt;color:#EFE7DA;white-space:nowrap;-webkit-text-stroke:.3pt #EFE7DA}}
.arows .a5{{position:static;display:flex;align-items:baseline;gap:2mm;padding:1.4mm 0;border-top:.15mm solid #3a332c}}
.arows .a5:last-child{{border-bottom:.15mm solid #3a332c}}
.arows .n{{font-family:Mono,monospace;font-size:7pt;letter-spacing:.06em;color:#D9773A;width:12mm;flex:none}}
.arows b{{font-family:{KO};font-weight:700;font-size:10pt;color:#EFE7DA;width:8mm;flex:none}}
.arows .d{{color:#6f665c;font-size:8pt}}
.arows .s{{font-family:{KO};font-size:9pt;color:#CFC6B8;white-space:nowrap}}
.rule5{{background:#D9773A}}
.b5{{font-family:{KO};font-size:8.6pt;line-height:14.5pt;color:#9A8F82;word-break:keep-all}}.b5 p{{white-space:normal}}
.end5{{font-family:{KO};font-size:10pt;line-height:16pt;color:#EFE7DA}}
"""


def html_doc():
    return (f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B19</title><style>{CSS}</style></head>"
            f"<body>{''.join(b18.sheets())}</body></html>")


def main():
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'plan_b19.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(html_doc())
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b19.pdf'), os.path.join(TMP, 'plan_b19')], check=True)


if __name__ == '__main__':
    main()
