"""블루엘리펀트 포트폴리오 마지막 쪽 — 사례(Thank you. · Contact, 밝은 회색 · 산세리프) 꼴로 사용자 연락처에 맞춤. 일러스트레이터용 벡터 (1920 × 1080 px).

  python3 tools/blue_elephant/thanks_page.py
    ->  docs/blue_elephant_portfolio/thanks/thanks_page.svg · .pdf (1920 × 1080 pt) · .png

사용자: "(사례) 사용자에 맞게 제작하고 일러스트로 제공하라."
연락처는 사용자 이력서의 CONTACT ME(전화 · 이메일). LinkedIn · Behance 같은 링크 줄은 없다 — 업무 유관 URL 은 생략하기로 함(10-30).
꼴 · 글자는 이력 쪽(resume_page.py)과 같게 맞춘다. 쪽 번호는 책 순서가 정해지지 않아 PAGE 로 둔다.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
FONTS = os.path.join(REPO, 'tools/p1_layout/fonts')
DIR = os.path.join(REPO, 'docs/blue_elephant_portfolio/thanks')
TMP = os.path.join(REPO, 'out/blue_elephant')
PRINT = os.path.join(REPO, 'tools/p1_layout/print_pdf.mjs')
W, H = 1920, 1080
PAGE = 'P/ 00'   # 책 순서가 정해지면 바꾼다
CONTACT = [('Name', 'Jeong Hyeokju'), ('Mail', 'aa3391@naver.com'), ('Phone', '+82 10-8582-3257')]
INK, GREY, LIGHT, BG = '#1E1E1E', '#6B6B6B', '#E4E4E4', '#F5F5F5'


def t(x, y, s, cls, anchor='start', extra=''):
    return f"<text x='{x}' y='{y}' class='{cls}' text-anchor='{anchor}'{extra}>{s}</text>"


def layers():
    rows = ''.join(t(1187, 586 + i * 21, k, 'lab') + t(1296, 586 + i * 21, v, 'val') for i, (k, v) in enumerate(CONTACT))
    return {
        'BACKGROUND': f"<rect x='0' y='0' width='{W}' height='{H}' fill='{BG}'/>",
        'TITLE': (t(176, 578, 'Thank you.', 'ghost', extra=" transform='translate(176 578) scale(.74 1) translate(-176 -578)'")
                  + t(236, 594, 'Thank you.', 'title')),
        'SIDE_TAB': (f"<g transform='translate(32 520) rotate(-90)'>{t(0, 0, PAGE, 'side', 'middle')}</g>"
                     f"<line x1='26' y1='557' x2='38' y2='557' stroke='#BDBDBD' stroke-width='1'/>"
                     f"<g transform='translate(32 610) rotate(-90)'>{t(0, 0, 'Contact', 'side', 'middle')}</g>"),
        'CONTACT': t(1187, 529, 'Contact', 'h2') + rows,
    }


def svg(fonts_inline=False):
    face = (f"@font-face{{font-family:'Instrument Sans';font-weight:400;src:url('file://{FONTS}/InstrumentSans-Regular.ttf')}}"
            f"@font-face{{font-family:'Instrument Sans';font-weight:700;src:url('file://{FONTS}/InstrumentSans-Bold.ttf')}}"
            f"@font-face{{font-family:'IBM Plex Mono';src:url('file://{FONTS}/IBMPlexMono-Regular.ttf')}}") if fonts_inline else ''
    groups = ''.join(f"\n  <g id='{k}'>{v}</g>" for k, v in layers().items())
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}px" height="{H}px" viewBox="0 0 {W} {H}">
  <defs><style>{face}
    text{{font-family:'Instrument Sans',sans-serif}}
    .ghost{{font-size:168px;font-weight:700;fill:{LIGHT}}}
    .title{{font-size:84px;font-weight:700;fill:{INK};letter-spacing:-1px}}
    .h2{{font-size:36px;font-weight:700;fill:{INK}}}
    .lab{{font-size:14.5px;font-style:italic;fill:{GREY}}}
    .val{{font-size:15px;fill:#4A4A4A}}
    .side{{font-family:'IBM Plex Mono',monospace;font-size:12px;fill:#9A9A9A;letter-spacing:1px}}
  </style></defs>{groups}
</svg>
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(DIR, exist_ok=True)
    out = os.path.join(DIR, 'thanks_page.svg')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(svg())
    h = os.path.join(TMP, 'thanks_page.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html><head><meta charset=utf-8><title>Thank you page</title><style>@page{{size:{W}pt {H}pt;margin:0}}"
                f"*{{margin:0;padding:0}}.sheet{{width:{W}pt;height:{H}pt;overflow:hidden}}.sheet svg{{display:block;width:{W}pt;height:{H}pt}}"
                f"</style></head><body><div class='sheet'>{svg(True).split('?>', 1)[1]}</div></body></html>")
    # 일러스트레이터는 1pt = 1px 로 읽으므로 PDF 쪽은 1920 × 1080 pt
    subprocess.run(['node', PRINT, h, os.path.join(DIR, 'thanks_page.pdf'), os.path.join(TMP, 'thanks_page')], check=True)
    from PIL import Image
    Image.open(os.path.join(TMP, 'thanks_page_1.png')).resize((W, H)).save(os.path.join(DIR, 'thanks_page.png'))
    print('wrote', out)


if __name__ == '__main__':
    main()
