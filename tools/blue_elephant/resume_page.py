"""블루엘리펀트 포트폴리오 이력 쪽 — 사례(Resume. · Education · Skills · Experiences, 밝은 회색 · 산세리프) 꼴로 사용자 이력에 맞춤.
일러스트레이터용 벡터 (1920 × 1080 px).

  python3 tools/blue_elephant/resume_page.py
    ->  docs/blue_elephant_portfolio/resume/resume_page.svg  (일러스트레이터에서 층별 벡터)
        docs/blue_elephant_portfolio/resume/resume_page.pdf  (1920 × 1080 pt = 일러스트레이터 1920 × 1080 px, 글꼴 포함)
        docs/blue_elephant_portfolio/resume/resume_page.png  (미리 보기)

사용자: "사용자의 이력서의 내용을 참고하여 사용자에게 맞추어진 1번 사례의 이미지를 제작하라. 일러스트 파일로 제공하라."
내용 출처: 사용자 이력서(JAJU 판 화면) — 학력 · 군 · 인턴(a.co.lab) · 카페 · 해비타트 · 스킬 6, 그리고 9쪽 캡션(Design Studio 2-1 · 2-2 · 4-1 · 4-2).
블루엘리펀트 지원이라 'JAJU 라운딩 VMD 지원' 줄과 VMD 말은 뺐다(사용자: "JAJU 는 배제한다").
스킬 아이콘은 회사 로고가 아니라 글자 두 자를 넣은 네모(사례의 칸 꼴).
영어 표기 중 확인 필요: 카페 가게 이름(뉴욕라츠오베이글스)의 영어 표기는 받지 못해 'CAFÉ' 로만, 전시 《돌봄의 디자인》은 'Design of Care' 로 옮김.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
FONTS = os.path.join(REPO, 'tools/p1_layout/fonts')
DIR = os.path.join(REPO, 'docs/blue_elephant_portfolio/resume')
TMP = os.path.join(REPO, 'out/blue_elephant')
PRINT = os.path.join(REPO, 'tools/p1_layout/print_pdf.mjs')
W, H = 1920, 1080

EDUCATION = [('University of Seoul', '2020 – present', ['Bachelor of Architecture (5-year program)', 'Seven design studios · 2D – 3D'])]
SKILLS_L = [('Ps', 'Photoshop', 'Retouching'), ('Ai', 'Illustrator', 'Vector graphics'), ('Id', 'InDesign', 'Editorial layout'),
            ('Ac', 'AutoCAD', '2D drawing'), ('Rh', 'Rhino', '3D modeling'), ('En', 'Enscape', 'Rendering')]  # 사용자 순서(11-03)
SKILLS_R = [('Ko', 'Korean', 'Native'), ('En', 'English', 'Research reading'), None, ('AI', 'AI imaging', 'Image generation'), ('CAM', 'Photography', '')]  # None = 빈 칸
EXPERIENCES = [
    ('A.CO.LAB', 'Architecture Office Intern  |  August 2026',
     ['Site survey and 3D modeling of the surrounding site and project buildings.',
      "Built a physical model shown at Culture Station Seoul 284, 'Design of Care'."]),
    ('UNIVERSITY OF SEOUL', 'Design Studio  |  2020 – 2026',
     ['Seven studios, from the city to the room: an urban plaza, a courtyard between buildings,',
      'a corridor joining two masses, and a section of the hollow beneath the city.']),
    ('CAFÉ', 'Part-time  |  August – November 2024',
     ['Built a grid storage system in the basement, sorting stock by item.',
      'Rearranged tables and plants in the hall to divide sightlines and open up the space.']),
    ('HABITAT FOR HUMANITY', 'Volunteer  |  2024 – 2025',
     ['Renovated an old home with new wallpaper and paint, working on site within a set budget.']),
    ('REPUBLIC OF KOREA ARMY', 'Sergeant  |  2022 – 2024',
     ['Completed full-term military service and received two commendations.']),
]

INK, GREY, LIGHT, BG = '#1E1E1E', '#6B6B6B', '#E4E4E4', '#F5F5F5'


def t(x, y, s, cls, anchor='start', extra=''):
    s = s.replace('&', '&amp;').replace("'", '&#39;')
    return f"<text x='{x}' y='{y}' class='{cls}' text-anchor='{anchor}'{extra}>{s}</text>"


def link_icon(x, y):
    return (f"<g transform='translate({x} {y}) scale(.55)' fill='none' stroke='#9A9A9A' stroke-width='2.2' stroke-linecap='round'>"
            "<path d='M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1'/><path d='M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1'/></g>")


def skill_box(x, y, mark):
    box = f"<rect x='{x}' y='{y}' width='34' height='34' rx='5' fill='none' stroke='{GREY}' stroke-width='1.6'/>"
    if mark == 'CAM':
        return box + (f"<g transform='translate({x + 7} {y + 7}) scale(.83)' fill='none' stroke='{GREY}' stroke-width='2'>"
                      "<rect x='2' y='6' width='20' height='14' rx='3'/><circle cx='12' cy='13' r='4'/><path d='M8 6l2-3h4l2 3'/></g>")
    return box + t(x + 17, y + 23.5, mark, 'mk', 'middle')


def layers():
    o = {}
    o['BACKGROUND'] = f"<rect x='0' y='0' width='{W}' height='{H}' fill='{BG}'/>"
    o['TITLE'] = (t(136, 228, 'Resume.', 'ghost', extra=" transform='translate(136 228) scale(.74 1) translate(-136 -228)'")
                  + t(192, 238, 'Resume.', 'title')
                  + t(196, 280, 'Jeong Hyeokju  —  Architecture · Photography · Style', 'sub'))
    o['SIDE_TAB'] = (f"<g transform='translate(32 512) rotate(-90)'>{t(0, 0, 'P/ 03', 'side', 'middle')}</g>"
                     f"<line x1='26' y1='545' x2='38' y2='545' stroke='#BDBDBD' stroke-width='1'/>"
                     f"<g transform='translate(32 590) rotate(-90)'>{t(0, 0, 'Resume', 'side', 'middle')}</g>")
    e = t(172, 368, 'Education', 'h2')
    y = 430
    for name, date, lines in EDUCATION:
        e += link_icon(150, y - 15) + t(172, y, name, 'h3') + t(172, y + 21, date, 'date')
        e += ''.join(t(172, y + 52 + i * 21, s, 'body') for i, s in enumerate(lines))
    o['EDUCATION'] = e
    s = t(172, 612, 'Skills', 'h2')
    for i, (m, n, d) in enumerate(SKILLS_L):
        yy = 652 + i * 46
        s += skill_box(172, yy, m) + t(231, yy + 22, n, 'sk') + t(346, yy + 22, d, 'skd')
    for i, item in enumerate(SKILLS_R):
        if item is None:
            continue
        m, n, d = item
        yy = 652 + i * 46
        s += skill_box(470, yy, m) + t(529, yy + 22, n, 'sk') + (t(644, yy + 22, d, 'skd') if d else '')
    o['SKILLS'] = s
    x = t(920, 178, 'Experiences', 'h2')
    for i, (org, role, lines) in enumerate(EXPERIENCES):
        y = 262 + i * 152
        x += t(920, y, org, 'org') + t(920, y + 25, role, 'role')
        x += ''.join(t(920, y + 60 + k * 20, line, 'body') for k, line in enumerate(lines))
    o['EXPERIENCES'] = x
    return o


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
    .title{{font-size:92px;font-weight:700;fill:{INK};letter-spacing:-1px}}
    .sub{{font-size:15px;fill:{GREY};letter-spacing:.3px}}
    .h2{{font-size:36px;font-weight:700;fill:{INK}}}
    .h3{{font-size:21px;font-weight:700;fill:{INK}}}
    .date,.role{{font-size:14.5px;font-style:italic;fill:{GREY}}}
    .body{{font-size:15px;fill:{GREY}}}
    .org{{font-size:20px;font-weight:700;fill:{INK};letter-spacing:.2px}}
    .sk{{font-size:15px;fill:#3A3A3A}}.skd{{font-size:12.5px;fill:#9A9A9A}}
    .mk{{font-size:17px;font-weight:700;fill:{GREY}}}
    .side{{font-family:'IBM Plex Mono',monospace;font-size:12px;fill:#9A9A9A;letter-spacing:1px}}
  </style></defs>{groups}
</svg>
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(DIR, exist_ok=True)
    out = os.path.join(DIR, 'resume_page.svg')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(svg())
    h = os.path.join(TMP, 'resume_page.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html><head><meta charset=utf-8><title>Resume page</title><style>@page{{size:{W}pt {H}pt;margin:0}}"
                f"*{{margin:0;padding:0}}.sheet{{width:{W}pt;height:{H}pt;overflow:hidden}}.sheet svg{{display:block;width:{W}pt;height:{H}pt}}"
                f"</style></head><body><div class='sheet'>{svg(True).split('?>', 1)[1]}</div></body></html>")
    # 일러스트레이터는 1pt = 1px 로 읽으므로 PDF 쪽은 1920 × 1080 pt
    subprocess.run(['node', PRINT, h, os.path.join(DIR, 'resume_page.pdf'), os.path.join(TMP, 'resume_page')], check=True)
    from PIL import Image
    Image.open(os.path.join(TMP, 'resume_page_1.png')).resize((W, H)).save(os.path.join(DIR, 'resume_page.png'))
    print('wrote', out)


if __name__ == '__main__':
    main()
