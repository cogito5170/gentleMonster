"""블루엘리펀트 SNS 쪽 — 겹친 아이폰 셋, 게시물 칸(아이디 줄 ~ 저장 표시)을 흰색으로 비운 판. 일러스트레이터용 벡터 (1920 × 1080 px).

  python3 tools/blue_elephant/sns_phones_blank.py
    ->  docs/blue_elephant_portfolio/sns_phones/sns_phones_blank.svg   (일러스트레이터에서 열면 휴대폰 · 화면 · 아이콘 · 글이 층별 벡터)
        docs/blue_elephant_portfolio/sns_phones/sns_phones_blank.pdf   (같은 그림, 글꼴 포함 — 일러스트레이터에서도 열림)
        docs/blue_elephant_portfolio/sns_phones/sns_phones_blank.png   (미리 보기)

사용자: "스크린의 좌측 상단 Jeonghyeokju 부터 우측 하단 저장 표시까지 화면을 흰색으로 변환하라. 3개의 화면 모두 진행한다.
1920x1080(픽셀) 크기의 일러스트 파일로 제공하라."
자리는 sns_phones.py 와 같다. 비운 칸은 이름 붙인 흰 사각형(POST AREA)으로 둬서 일러스트레이터에서 그 위에 쪽을 얹거나 클리핑 마스크로 쓴다.
.ai 고유 형식은 이 환경에서 만들 수 없어 SVG(일러스트레이터 기본 지원) · PDF 로 낸다.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
FONTS = os.path.join(REPO, 'tools/p1_layout/fonts')
DIR = os.path.join(REPO, 'docs/blue_elephant_portfolio/sns_phones')
TMP = os.path.join(REPO, 'out/blue_elephant')
PRINT = os.path.join(REPO, 'tools/p1_layout/print_pdf.mjs')
W, H = 1920, 1080
BAR, STORIES, NAV = 0, 163, 62          # 화면 위에서 스토리 줄 끝까지 163px, 아래 메뉴 62px
PHONES = [('LEFT', 452, 196, 370, 768), ('RIGHT', 1098, 196, 370, 768), ('CENTER', 755, 236, 410, 826)]  # 뒤 → 앞

I = {  # 24 × 24 선 아이콘 (sns_phones.py 와 같음)
    'cam': "<rect x='3' y='6' width='18' height='14' rx='4'/><circle cx='12' cy='13' r='4'/><circle cx='17.5' cy='9' r='.6' fill='#111'/>",
    'add': "<circle cx='10' cy='8' r='4'/><path d='M3 21c0-4 3-6 7-6s7 2 7 6'/><path d='M19 7v6M16 10h6'/>",
    'heart': "<path d='M12 20s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 9c0 6-8 11-8 11z'/>",
    'home': "<path fill='#111' d='M3 11l9-8 9 8v10h-6v-6H9v6H3z'/>",
    'search': "<circle cx='11' cy='11' r='7'/><path d='M16 16l5 5'/>",
    'plus': "<rect x='3' y='3' width='18' height='18' rx='5'/><path d='M12 8v8M8 12h8'/>",
    'user': "<circle cx='12' cy='8' r='4'/><path d='M4 21c0-4 4-6 8-6s8 2 8 6'/>",
}


def icon(name, x, y, size):
    s = size / 24
    return (f"<g transform='translate({x:.1f} {y:.1f}) scale({s:.4f})' fill='none' stroke='#111' stroke-width='1.7' "
            f"stroke-linecap='round' stroke-linejoin='round'>{I[name]}</g>")


def phone(name, x, y, w, h):
    sx, sy, sw, sh = x + 10, y + 10, w - 20, h - 20
    cid = f'clip-{name}'
    post_y, post_h = sy + STORIES, sh - STORIES - NAV
    nav_y = sy + sh - NAV
    av_cx, av_cy = sx + 18 + 23, sy + 78 + 23
    nav = ''.join(icon(n, sx + sw * (i + .5) / 5 - 12, nav_y + 14, 24) for i, n in enumerate(['home', 'search', 'plus', 'heart', 'user']))
    return f"""
  <g id="PHONE_{name}">
    <rect id="BODY_{name}" x="{x}" y="{y}" width="{w}" height="{h}" rx="52" fill="#FFFFFF" stroke="#D9D9D9" stroke-width="1.5" filter="url(#shadow)"/>
    <clipPath id="{cid}"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="42"/></clipPath>
    <g id="SCREEN_{name}" clip-path="url(#{cid})">
      <rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="#FFFFFF"/>
      <g id="TOPBAR_{name}">
        {icon('cam', sx + 20, sy + 33, 22)}
        <text x="{sx + sw / 2:.1f}" y="{sy + 52}" text-anchor="middle" class="logo">Instagram</text>
        {icon('add', sx + sw - 42, sy + 33, 22)}
      </g>
      <g id="STORIES_{name}">
        <circle cx="{av_cx}" cy="{av_cy}" r="22" fill="none" stroke="url(#ring)" stroke-width="2.4"/>
        <circle cx="{av_cx}" cy="{av_cy}" r="18.5" fill="#E9E6E1"/>
        <text x="{av_cx}" y="{sy + 138}" text-anchor="middle" class="small">Your Story</text>
        <text x="{sx + sw - 18}" y="{sy + 92}" text-anchor="end" class="watch">Watch All</text>
        <line x1="{sx}" y1="{post_y - .5}" x2="{sx + sw}" y2="{post_y - .5}" stroke="#EFEFEF" stroke-width="1"/>
      </g>
      <rect id="POST_AREA_{name}" x="{sx}" y="{post_y}" width="{sw}" height="{post_h}" fill="#FFFFFF"/>
      <g id="NAV_{name}">
        <line x1="{sx}" y1="{nav_y + .5}" x2="{sx + sw}" y2="{nav_y + .5}" stroke="#EFEFEF" stroke-width="1"/>
        {nav}
      </g>
    </g>
  </g>"""


def svg(fonts_inline=False):
    face = (f"@font-face{{font-family:'Lora';font-style:italic;font-weight:700;src:url('file://{FONTS}/Lora-Italic.ttf')}}"
            f"@font-face{{font-family:'Instrument Sans';font-weight:400;src:url('file://{FONTS}/InstrumentSans-Regular.ttf')}}"
            f"@font-face{{font-family:'Instrument Sans';font-weight:700;src:url('file://{FONTS}/InstrumentSans-Bold.ttf')}}") if fonts_inline else ''
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}px" height="{H}px" viewBox="0 0 {W} {H}">
  <defs>
    <style>{face}
      .logo{{font-family:'Lora',serif;font-style:italic;font-weight:700;font-size:22px;fill:#111}}
      .small{{font-family:'Instrument Sans',sans-serif;font-size:10px;fill:#333}}
      .watch{{font-family:'Instrument Sans',sans-serif;font-weight:700;font-size:11px;fill:#111}}
    </style>
    <linearGradient id="ring" x1="0" y1="1" x2="1" y2="0">
      <stop offset="0" stop-color="#F9CE34"/><stop offset=".5" stop-color="#EE2A7B"/><stop offset="1" stop-color="#6228D7"/>
    </linearGradient>
    <filter id="shadow" x="-30%" y="-20%" width="160%" height="150%">
      <feDropShadow dx="0" dy="30" stdDeviation="30" flood-color="#000" flood-opacity=".55"/>
    </filter>
  </defs>
  <rect id="BACKGROUND" x="0" y="0" width="{W}" height="{H}" fill="#0A0A0A"/>
  <rect id="LOGO_AREA" x="860" y="40" width="200" height="150" fill="none"/>{''.join(phone(*p) for p in PHONES)}
</svg>
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    out = os.path.join(DIR, 'sns_phones_blank.svg')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(svg())
    h = os.path.join(TMP, 'sns_phones_blank.html')
    body = svg(True).split('?>', 1)[1]
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html><head><meta charset=utf-8><title>SNS phones blank</title><style>@page{{size:{W}pt {H}pt;margin:0}}"
                f"*{{margin:0;padding:0}}.sheet{{width:{W}pt;height:{H}pt;overflow:hidden}}.sheet svg{{display:block;width:{W}pt;height:{H}pt}}</style></head>"
                f"<body><div class='sheet'>{body}</div></body></html>")
    # 일러스트레이터는 1pt = 1px 로 읽으므로 PDF 쪽은 1920 × 1080 pt
    subprocess.run(['node', PRINT, h, os.path.join(DIR, 'sns_phones_blank.pdf'), os.path.join(TMP, 'sns_blank')], check=True)
    os.replace(os.path.join(TMP, 'sns_blank_1.png'), os.path.join(DIR, 'sns_phones_blank.png'))
    print('wrote', out)


if __name__ == '__main__':
    main()
