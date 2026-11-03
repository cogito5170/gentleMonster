"""블루엘리펀트 포트폴리오 SNS 쪽 — 사용자 인스타그램 카드 셋을 겹친 아이폰 셋으로 (1920 × 1080, 검은 바탕).

  python3 tools/blue_elephant/sns_phones.py   ->  docs/blue_elephant_portfolio/sns_phones/sns_phones.pdf · sns_phones.png

사용자: "2번의 이미지(인스타그램 카드 셋)를 1번(TV Azteca 인스타그램 목업)의 디자인 스타일로 전환하라.
1. 최상단 로고는 비워둘 것  2. 3개의 아이폰 디자인 안에 각 페이지가 들어갈 것  3. 아이폰이 사례와 같이 겹쳐 있을 것  4. 배경은 검은색 바탕."
사례에서 가져온 것: 흰 둥근 휴대폰 셋 — 가운데가 앞에 크게, 양옆은 뒤에서 조금 위로 · 가운데에 겹침, 휴대폰 안은 인스타그램 화면
  (맨 위 줄 · 스토리 · 게시물 머리 · 사진 · 반응 아이콘 · 아래 메뉴), 맨 위 가운데 로고 자리(비워 둠).
사진: 사용자 카드에서 잘라 낸 게시물 사진 셋(post_left · post_grid · post_right). 좋아요 수 · 댓글 같은 지어낸 숫자 · 글은 넣지 않았다.
아이콘은 선으로 그린 UI 표시일 뿐 그림이 아니다.
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
HANDLE = 'Jeonghyeokju'
CHROME = 312   # 맨 위 줄 · 스토리 · 게시물 머리 · 반응 줄 · 아래 메뉴의 높이 합(px)

I = {  # 24 × 24 선 아이콘
    'cam': "<rect x='3' y='6' width='18' height='14' rx='4'/><circle cx='12' cy='13' r='4'/><circle cx='17.5' cy='9' r='.6' class='f'/>",
    'add': "<circle cx='10' cy='8' r='4'/><path d='M3 21c0-4 3-6 7-6s7 2 7 6'/><path d='M19 7v6M16 10h6'/>",
    'heart': "<path d='M12 20s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 9c0 6-8 11-8 11z'/>",
    'heartf': "<path class='red' d='M12 20s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 9c0 6-8 11-8 11z'/>",
    'chat': "<path d='M20 12a8 8 0 1 1-3.4-6.5A8 8 0 0 1 20 12z'/><path d='M20 20l-1.8-3.6'/>",
    'repost': "<path d='M5 10V8a2 2 0 0 1 2-2h11l-3-3M19 14v2a2 2 0 0 1-2 2H6l3 3'/>",
    'send': "<path d='M21 3L10 14M21 3l-7 18-4-7-7-4z'/>",
    'save': "<path d='M6 3h12v18l-6-5-6 5z'/>",
    'home': "<path class='k' d='M3 11l9-8 9 8v10h-6v-6H9v6H3z'/>",
    'search': "<circle cx='11' cy='11' r='7'/><path d='M16 16l5 5'/>",
    'plus': "<rect x='3' y='3' width='18' height='18' rx='5'/><path d='M12 8v8M8 12h8'/>",
    'user': "<circle cx='12' cy='8' r='4'/><path d='M4 21c0-4 4-6 8-6s8 2 8 6'/>",
}


def ic(name, size=22):
    return f"<svg class='ic' width='{size}' height='{size}' viewBox='0 0 24 24'>{I[name]}</svg>"


def avatar(size):
    return f"<span class='av' style='width:{size}px;height:{size}px'><i></i></span>"


def phone(x, y, w, h, img, z, aspect):
    """흰 휴대폰 한 대. aspect = 사진 높이 / 너비."""
    sw = w - 20
    ph = min(round(sw * aspect), h - 20 - CHROME)     # 반응 줄이 아래 메뉴에 가리지 않게
    screen = (f"<div class='bar'>{ic('cam')}<b class='logo'>Instagram</b>{ic('add')}</div>"
              f"<div class='stories'><div class='st'>{avatar(46)}<small>Your Story</small></div><span class='watch'>Watch All</span></div>"
              f"<div class='head'>{avatar(26)}<b>{HANDLE.lower()}</b><span class='vf'></span><span class='dots'>···</span></div>"
              f"<div class='photo' style='height:{ph}px;background-image:url(\"file://{os.path.join(DIR, img)}\")'></div>"
              f"<div class='acts'>{ic('heartf')}{ic('chat')}{ic('repost')}{ic('send')}<span class='sp'></span>{ic('save')}</div>"
              f"<div class='nav'>{ic('home', 24)}{ic('search', 24)}{ic('plus', 24)}{ic('heart', 24)}{ic('user', 24)}</div>")
    return (f"<div class='phone' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px;z-index:{z}'>"
            f"<div class='screen'>{screen}</div></div>")


def page():
    return (phone(452, 196, 370, 768, 'post_left.jpg', 1, 379 / 305)
            + phone(1098, 196, 370, 768, 'post_right.jpg', 1, 378 / 305)
            + phone(755, 236, 410, 826, 'post_grid.jpg', 3, 475 / 378))


CSS = f"""
@font-face{{font-family:Inst;font-weight:400;src:url('file://{FONTS}/InstrumentSans-Regular.ttf')}}
@font-face{{font-family:Inst;font-weight:700;src:url('file://{FONTS}/InstrumentSans-Bold.ttf')}}
@font-face{{font-family:Lora;font-style:italic;font-weight:700;src:url('file://{FONTS}/Lora-Italic.ttf')}}
@page{{size:{W}px {H}px;margin:0}}*{{margin:0;padding:0;box-sizing:border-box}}
.sheet{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#0A0A0A}}
.phone{{position:absolute;background:#fff;border-radius:52px;padding:10px;border:1.5px solid #D9D9D9;
  box-shadow:0 30px 60px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.08)}}
.screen{{position:relative;width:100%;height:100%;border-radius:42px;overflow:hidden;background:#fff;font-family:Inst,sans-serif;color:#111}}
.ic{{fill:none;stroke:#111;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;flex:none}}.ic .f{{fill:#111}}.ic .k{{fill:#111}}
.ic .red{{fill:#E1262C;stroke:#E1262C}}
.bar{{display:flex;align-items:center;justify-content:space-between;padding:34px 20px 10px}}
.logo{{font-family:Lora,serif;font-style:italic;font-weight:700;font-size:22px;letter-spacing:-.01em}}
.stories{{display:flex;align-items:flex-start;justify-content:space-between;padding:4px 18px 10px;border-bottom:1px solid #EFEFEF}}
.st{{display:flex;flex-direction:column;align-items:center;gap:3px}}.st small{{font-size:10px;color:#333}}
.watch{{font-size:11px;font-weight:700;color:#111;margin-top:2px}}
.av{{display:inline-block;border-radius:50%;padding:2px;background:conic-gradient(#F9CE34,#EE2A7B,#6228D7,#F9CE34)}}
.av i{{display:block;width:100%;height:100%;border-radius:50%;background:#fff;border:2px solid #fff;box-shadow:inset 0 0 0 30px #E9E6E1}}
.head{{display:flex;align-items:center;gap:7px;padding:9px 14px}}.head b{{font-size:12px}}
.vf{{width:10px;height:10px;border-radius:50%;background:#3897F0}}.dots{{margin-left:auto;font-weight:700;letter-spacing:1px}}
.photo{{width:100%;background-size:cover;background-position:center}}
.acts{{display:flex;align-items:center;gap:13px;padding:11px 14px}}.sp{{flex:1}}
.nav{{position:absolute;left:0;right:0;bottom:0;height:62px;display:flex;align-items:center;justify-content:space-around;
  padding-bottom:10px;border-top:1px solid #EFEFEF;background:#fff}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'sns_phones.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=en><head><meta charset=utf-8><title>SNS phones</title><style>{CSS}</style></head>"
                f"<body><div class='sheet'>{page()}</div></body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(DIR, 'sns_phones.pdf'), os.path.join(TMP, 'sns_phones')], check=True)
    os.replace(os.path.join(TMP, 'sns_phones_1.png'), os.path.join(DIR, 'sns_phones.png'))


if __name__ == '__main__':
    main()
