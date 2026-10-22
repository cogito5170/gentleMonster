"""JAJU 포트폴리오 2쪽 — 사용자가 준 사례('Behind the Scenes, Beyond the Ordinary' 리포타주 쪽)를 따라 다시 짠 메시지 쪽.

  python3 tools/jaju_layout/p02_reportage.py   ->  docs/jaju_rounding_vmd/layout/p02_reportage.pdf

사례의 문법: 어두운 사진 한 장이 쪽 왼쪽 2/3 를 차지하고(인물이 왼쪽 끝에서 잘림), 오른쪽 1/3 은 같은 어둠이 이어진 글 단.
  글 단 = 작은 고정폭 회색 표지 글(REPORTAGE / INFORMATION) → 가는 세리프 크림색 제목 두 줄 → 고정폭 대문자 크림색 부제 한 줄
          → 회색 대문자 본문 두 문단. 쪽 양 가장자리에 필름 가장자리 같은 아주 옅은 숫자.
옮긴 것: 사진(opening_book_dark.jpg)을 왼쪽으로 밀어 책 속 사진 · 마네킹 · 인물이 왼쪽 2/3 에, 오른쪽 밝은 책장은 검정으로 녹여 글 단.
  표지 글 PROLOGUE / FROM THE INSIDE → 제목 '밖에서 보면 상품이 보이고, / 안에서 보면 사람이 보인다.' → 부제 A VMD WHO LOOKS OUT FROM THE INSIDE
  → 한국어 두 문단(보는 자리 세 문장 / 멈추고 웃는 사람 네 문장) → 영어 대문자 한 문단(사례의 대문자 본문).
최종 글꼴: 제목 명조 Noto Serif KR Light(사례의 가는 세리프), 본문 Pretendard, 표지 글 · 부제 IBM Plex Mono, 영어 Instrument Sans.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import p02_photo_text_options as pt  # noqa: E402  (BOOK-DARK 경로)

opt, pe = pt.opt, pt.pe
t, div, photo = pe.t, pe.div, pe.photo
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT
KO, EN = opt.KO, opt.EN
INK = '#0D0E10'


def edge_numbers():
    """필름 가장자리처럼 양옆에 아주 옅은 숫자."""
    o = []
    for i, y in enumerate(range(14, 200, 16)):
        o.append(t(2.2, y, 8, 3, f'{i * 4 + 2:02d}', 'edge'))
        o.append(t(288, y + 8, 8, 3, f'{i * 4 + 4:02d}', 'edge'))
    return ''.join(o)


def page():
    ko1 = ' '.join(KO[:3])
    ko2 = ' '.join(KO[3:6]) + f" <span class='cr'>{KO[6]}</span>"
    return ''.join([
        photo('BOOK-DARK', -64, 0, 320, 210, focus=(0.5, 0.5)),
        div(0, 0, 297, 210, '', 'fadeR'),
        t(170, 54, 110, 4, 'PROLOGUE&nbsp;&nbsp;/&nbsp;&nbsp;FROM THE INSIDE', 'r-lab'),
        t(170, 62, 115, 30, '<p>밖에서 보면 상품이 보이고,</p><p>안에서 보면 사람이 보인다.</p>', 'r-head'),
        t(170, 88, 115, 5, 'A VMD WHO LOOKS OUT FROM THE INSIDE', 'r-sub'),
        t(170, 104, 92, 30, f'<p>{ko1}</p>', 'r-body wrap'),
        t(170, 126, 92, 36, f'<p>{ko2}</p>', 'r-body wrap'),
        t(170, 158, 92, 40, f'<p>{EN.upper()}</p>', 'r-en wrap'),
        edge_numbers(),
    ])


KOF = opt.KOF
CSS = opt.CSS + f"""
.sheet.rep{{background:{INK}}}
.fadeR{{background:linear-gradient(to right,rgba(13,14,16,0) 46%,rgba(13,14,16,.86) 54%,rgba(13,14,16,1) 60%),
        linear-gradient(to bottom,rgba(13,14,16,.5),rgba(13,14,16,.22) 22%,rgba(13,14,16,.22) 70%,rgba(13,14,16,.6))}}
.r-lab{{font-family:Mono,monospace;font-size:6.4pt;letter-spacing:.06em;color:#8E8C88;white-space:nowrap}}
.r-head{{font-family:{KOF};font-size:19pt;line-height:26pt;color:#EFE3CB;letter-spacing:-.01em}}
.r-sub{{font-family:Mono,monospace;font-size:7.4pt;letter-spacing:.08em;color:#E4D6BA;white-space:nowrap}}
.r-body{{font-family:{KOF};font-size:8.4pt;line-height:14pt;color:#A9A7A2;word-break:keep-all}}.r-body p{{white-space:normal}}
.r-body .cr{{color:#EFE3CB}}
.r-en{{font-family:Inst,sans-serif;font-size:6.2pt;line-height:9.4pt;letter-spacing:.02em;color:#7C7A76}}.r-en p{{white-space:normal}}
.edge{{font-family:Mono,monospace;font-size:3.6pt;color:rgba(239,227,203,.16);transform:rotate(90deg);transform-origin:0 0;white-space:nowrap}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'p02_reportage.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU p02 reportage</title><style>{CSS}</style></head>"
                f"<body><div class='sheet rep'>{page()}</div></body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'p02_reportage.pdf'), os.path.join(TMP, 'p02_rep')], check=True)


if __name__ == '__main__':
    main()
