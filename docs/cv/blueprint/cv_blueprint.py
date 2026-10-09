"""CV 1/2 layout blueprint: design ref (1) DVSY homepage grammar + CV content map, on an A3 landscape sheet.

Writes cv_blueprint.svg next to this file; Inkscape exports the PDF:
    python3 docs/cv/blueprint/cv_blueprint.py
    inkscape docs/cv/blueprint/cv_blueprint.svg --export-type=pdf --export-filename=docs/cv/blueprint/cv_blueprint.pdf
Units are mm. Inside the A4 drawing every size is the real printed size; the group is drawn at 86 %.
Text marked ____ is a fact the applicant fills in. Nothing here is invented.
"""
from html import escape
from pathlib import Path

PT = 0.3528  # 1 pt in mm
SANS = "Inter, 'Noto Sans CJK KR', sans-serif"
KR = "'Noto Sans CJK KR', Inter, sans-serif"

# tone of reference (1), sampled from the image
BG, CARD, PHOTO, PHOTO_X = "#0B0B0B", "#1E1E1E", "#2E2E2E", "#454545"
TEXT, SUB, LINE = "#ECE8E1", "#8E8B86", "#3A3A3A"
INK, INK2, RULE = "#15191B", "#5B656B", "#C5CDD1"  # sheet (repo blueprint tone)

out = []
w = out.append


def t(x, y, s, pt=6, fill=TEXT, weight=400, anchor="start", fam=SANS, ls=0, op=1):
    w(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{fam}" font-size="{pt * PT:.3f}" font-weight="{weight}" '
      f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls:.3f}" opacity="{op}">{escape(s)}</text>')


def lines(x, y, rows, pt=5.4, lh=1.45, **k):
    for i, s in enumerate(rows):
        t(x, y + i * pt * PT * lh * 1.0, s, pt, **k)


def r(x, y, wd, h, fill="none", stroke="none", sw=0.25, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    w(f'<rect x="{x:.2f}" y="{y:.2f}" width="{wd:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def ln(x1, y1, x2, y2, stroke=INK, sw=0.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    w(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def photo(x, y, wd, h, tag, note, rx=1.6, at=None):
    r(x, y, wd, h, PHOTO, rx=rx)
    ln(x, y, x + wd, y + h, PHOTO_X, 0.25); ln(x + wd, y, x, y + h, PHOTO_X, 0.25)
    cx, cy = at or (x + wd / 2, y + h / 2)
    r(cx - 30, cy - 5, 60, 10, PHOTO, rx=1)
    t(cx, cy - 0.6, tag, 6, TEXT, 600, "middle", ls=0.3)
    t(cx, cy + 3.2, note, 5.2, SUB, 400, "middle", KR)


def arrow(cx, cy, label, rr=1.9):
    w(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="{SUB}" stroke-width="0.25"/>')
    ln(cx - 0.7, cy + 0.7, cx + 0.7, cy - 0.7, TEXT, 0.25)
    ln(cx - 0.1, cy - 0.7, cx + 0.7, cy - 0.7, TEXT, 0.25); ln(cx + 0.7, cy - 0.7, cx + 0.7, cy + 0.1, TEXT, 0.25)
    t(cx + rr + 1.4, cy + 0.7, label, 4.8, TEXT, 500, fam=SANS, ls=0.15)


def card(x, y, wd, h, title, body, slot=None, body_pt=5.4):
    r(x, y, wd, h, CARD, rx=1.6)
    t(x + 4, y + 5.4, title, 6, TEXT, 600, ls=0.25)
    lines(x + 4, y + 9.6, body, body_pt, fill=SUB, fam=KR)
    if slot:
        arrow(x + wd - 20, y + h / 2, slot)


# ---------------------------------------------------------------- A4 page (CV 1/2), real mm
def a4():
    M, CW = 7, 196
    r(0, 0, 210, 297, BG)
    # (1) NAV
    t(M + 1, 12.6, "JEONG HYEOKJU", 7, TEXT, 600, ls=0.35)
    x = 203
    pills = ["CONTACT", "SKILLS", "EXPERIENCE", "EDUCATION", "ABOUT"]
    for i, p in enumerate(pills):
        pw = len(p) * 1.55 + 4.4
        x -= pw
        if i == 0:
            r(x, 8.8, pw, 4.6, "url(#hatch)", TEXT, 0.25, 0.8, "0.6 0.4")
        else:
            r(x, 8.8, pw, 4.6, CARD, rx=0.8)
        t(x + pw / 2, 11.9, p, 4.6, TEXT, 600, "middle", ls=0.2)
        x -= 1.4
    # (2) HERO
    photo(M, 17, CW, 72, "PHOTO 01", "인물 사진 ____ (흑백 또는 저채도)", at=(168, 28))
    t(15, 50, "JEONG", 51, TEXT, 100, ls=1.6)
    t(15, 69, "HYEOKJU", 51, TEXT, 100, ls=1.6)
    t(16, 77.5, "SPATIAL DESIGNER  ·  공간 설계 디자이너", 6.4, TEXT, 500, fam=SANS, ls=0.2)
    t(16, 81.4, "건물을 설계하던 감각으로 매장을 설계하려는 건축학도", 5.6, SUB, 400, fam=KR)
    arrow(170, 80, "PAGE 2 · 자기소개서")
    # (3) four cards = strengths (cover letter Q2)
    cw = (CW - 3 * 2.5) / 4
    cards = [("01  PLANNING", "기획", ["리서치·분석으로 컨셉을 세우고", "건물로 발전시킨 설계 7학기"]),
             ("02  MAKING · TELLING", "구현과 소통", ["2D 도면 → 3D 모델링 →", "시각화 → 후보정"]),
             ("03  SENSE", "디자인 감각", ["시선을 끄는 색과", "한발 물러서는 색"]),
             ("04  RESTRAINT + BOLD", "절제와 과감", ["건축에서 익힌 절제 위에", "과감을 더한다"])]
    for i, (en, ko, body) in enumerate(cards):
        x = M + i * (cw + 2.5)
        r(x, 91, cw, 26, CARD, rx=1.6)
        t(x + 3.5, 96.4, en, 5.6, TEXT, 600, ls=0.2)
        t(x + 3.5, 100.2, ko, 5.2, SUB, 500, fam=KR)
        lines(x + 3.5, 105, body, 5.0, fill=SUB, fam=KR)
        arrow(x + 5.4, 112.6, "P.2", 1.7)
    # (4) numbers
    stats = [("5-YEAR B.ARCH", "5", "5년제 건축학과"), ("DESIGN STUDIOS", "7", "설계 수업 7학기"),
             ("TOOLS", "6", "2D · 3D · 후보정"), ("INTERNSHIP", "1", "건축사사무소")]
    for i, (lab, n, ko) in enumerate(stats):
        x = M + 1 + i * 49.5
        t(x, 123, lab, 4.8, SUB, 500, ls=0.25)
        t(x, 131, n, 17, TEXT, 200)
        t(x + 7.5, 131, ko, 5, SUB, 400, fam=KR)
    # (5) ABOUT
    hw = (CW - 2.5) / 2
    r(M, 135, hw, 46, CARD, rx=1.6)
    t(M + 5, 141.5, "ABOUT", 5, TEXT, 600, ls=0.3)
    t(M + 5, 150.5, "틀을 배우고,", 11, TEXT, 300, fam=KR)
    t(M + 5, 156, "그 안을 채우는 건축학도", 11, TEXT, 300, fam=KR)
    t(M + 5, 164.5, "PROFILE", 4.8, TEXT, 600, ls=0.25)
    lines(M + 5, 168.6, ["5년제 건축학과 · 4학년 2학기 휴학", "건축사사무소 인턴을 거쳐", "공간 디자인으로 전향"], 5.2, fill=SUB, fam=KR)
    t(M + 50, 164.5, "INTERESTS", 4.8, TEXT, 600, ls=0.25)
    lines(M + 50, 168.6, ["패션 · 갤러리", "가구와 조명 수집", "건축물의 실내 마감재와 마감 방식"], 5.2, fill=SUB, fam=KR)
    photo(M + hw + 2.5, 135, hw, 46, "PHOTO 02", "____ (공간 · 마감재 · 오브제)")
    # (6) section title
    t(M + 1, 191, "EDUCATION & EXPERIENCE", 14, TEXT, 300, ls=0.3)
    # (7) checkerboard
    rh, ch = 46.75, (46.75 - 2.5) / 2
    yA, yB = 194, 194 + rh + 2.5
    x2 = M + hw + 2.5
    photo(M, yA, hw, rh, "PHOTO 03", "____ (작업 이미지 · 모델링 · 렌더)")
    card(x2, yA, hw, ch, "EDUCATION", ["____대학교 건축학과 (5년제)", "4학년 2학기 휴학 중"], "____ – ____")
    card(x2, yA + ch + 2.5, hw, ch, "EXPERIENCE", ["건축사사무소 ____ · 인턴", "현장 실측 · 모델링 · 주변 대지와", "프로젝트 건물 구현"], "____")
    card(M, yB, hw, ch, "SKILLS", ["AutoCAD · Rhino · Enscape", "Photoshop · Illustrator · InDesign", "LANGUAGE ____"], "6 TOOLS")
    card(M, yB + ch + 2.5, hw, ch, "CONTACT", ["T  ____", "E  ____", "PORTFOLIO  ____"], "GET IN TOUCH")
    photo(x2, yB, hw, rh, "PHOTO 04", "____ (02 PICTURE 사진 중)")


# zone bands in A4 mm: (tag, name, y0, y1)
ZONES = [("1", "NAV", 7, 15), ("2", "HERO", 17, 89), ("3", "CARDS ×4", 91, 117), ("4", "NUMBERS", 119, 133),
         ("5", "ABOUT", 135, 181), ("6", "TITLE", 183, 192), ("7", "GRID 2×2", 194, 290)]


def tag(cx, cy, n, rr=2.3):
    w(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rr}" fill="{INK}"/>')
    t(cx, cy + 0.95, n, 7, "#FFFFFF", 700, "middle")


# ---------------------------------------------------------------- sheet
S, OX, OY = 0.86, 24, 26
w('<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">')
w('<defs><pattern id="hatch" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
  f'<rect width="1.2" height="1.2" fill="#262626"/><line x1="0" y1="0" x2="0" y2="1.2" stroke="{SUB}" stroke-width="0.4"/></pattern>'
  '<marker id="ar" viewBox="0 0 6 6" refX="3" refY="3" markerWidth="3" markerHeight="3" orient="auto-start-reverse">'
  f'<path d="M0,0 L6,3 L0,6 z" fill="{INK}"/></marker></defs>')
r(0, 0, 420, 297, "#FFFFFF")
r(6, 6, 408, 285, stroke=INK, sw=0.5)

# drawing caption
t(OX, 13, "A-01   CV 1/2 · LAYOUT", 9, INK, 700, ls=0.3)
t(OX, 17.6, "디자인 레퍼런스 ① DVSY의 홈페이지 문법에 CV 항목을 넣은 A4 세로 지면. 86 % 축척, 치수는 실제 mm.", 6, INK2, 400, fam=KR)

w(f'<g transform="translate({OX},{OY}) scale({S})">')
a4()
w('</g>')

def D(v):
    return v * S
# overall dimensions
ln(OX, OY - 3.5, OX + D(210), OY - 3.5, INK, 0.2); w(f'<line x1="{OX}" y1="{OY - 3.5}" x2="{OX + D(210)}" y2="{OY - 3.5}" stroke="{INK}" stroke-width="0.2" marker-start="url(#ar)" marker-end="url(#ar)"/>')
t(OX + D(105), OY - 4.6, "210", 6, INK, 500, "middle")
w(f'<line x1="{OX - 4}" y1="{OY}" x2="{OX - 4}" y2="{OY + D(297)}" stroke="{INK}" stroke-width="0.2" marker-start="url(#ar)" marker-end="url(#ar)"/>')
w(f'<text transform="translate({OX - 5.2},{OY + D(148.5)}) rotate(-90)" font-family="{SANS}" font-size="{6 * PT}" fill="{INK}" text-anchor="middle" font-weight="500">297</text>')
# margin 7
ln(OX, OY + D(297) + 2.5, OX + D(7), OY + D(297) + 2.5, INK, 0.2)
t(OX + D(3.5), OY + D(297) + 5.8, "7", 5.2, INK2, 400, "middle")
t(OX + D(7) + 2, OY + D(297) + 5.8, "여백 7 · 사이 2.5 · 모서리 R1.6 · 반폭 96.75", 5.2, INK2, 400, fam=KR)
# zone bands
zx = OX + D(210) + 3
for n, name, y0, y1 in ZONES:
    a, b = OY + D(y0), OY + D(y1)
    ln(zx, a, zx + 2, a, INK, 0.2); ln(zx, b, zx + 2, b, INK, 0.2); ln(zx + 1, a, zx + 1, b, INK, 0.2)
    tag(zx + 5.5, (a + b) / 2, n)
    t(zx + 8.8, (a + b) / 2 - 0.2, name, 5.4, INK, 600, ls=0.2)
    t(zx + 8.8, (a + b) / 2 + 2.4, f"{y1 - y0:g}", 5.2, INK2, 400)

# ---------------------------------------------------------------- content map (middle)
MX = 237
ln(MX - 4, 10, MX - 4, 287, INK, 0.3)
t(MX, 15, "CONTENT MAP", 9, INK, 700, ls=0.3)
t(MX, 20.5, "레퍼런스 ① 의 요소 → CV 내용. ✓ 확인된 사실 · ____ 혁주님이 채울 칸", 6, INK2, 400, fam=KR)
cols = [MX, MX + 7, MX + 33, MX + 82]
y = 27
for i, h in enumerate(["", "레퍼런스 ① DVSY", "CV 내용", "상태"]):
    t(cols[i], y, h, 5.6, INK, 700, fam=KR)
ln(MX, y + 1.6, MX + 108, y + 1.6, INK, 0.3)
MAP = [
    ("1", ["로고", "메뉴 알약 4", "강조 버튼"], ["이름 로고 JEONG HYEOKJU", "ABOUT · EDUCATION · EXPERIENCE · SKILLS", "강조 버튼 = CONTACT (빗금 = 색 미정)"], ["✓ 구조", "강조색 미정"]),
    ("2", ["풀블리드 사진", "얇은 대형 헤드라인", "서브 카피 · LEARN MORE"], ["인물 사진 (PHOTO 01)", "JEONG / HYEOKJU", "직무 + 정체성 문장", "→ PAGE 2 자기소개서"], ["사진 ____", "정체성 문장 퇴고 중"]),
    ("3", ["가치 카드 4", "제목 · 두 줄 · 화살표"], ["강점 4: 기획 · 구현과 소통 ·", "디자인 감각 · 절제와 과감", "(자기소개서 문항 2에서)", "화살표 → P.2 해당 문단"], ["✓ 원고 있음"]),
    ("4", ["실적 숫자 4", "150+ · 500+ …"], ["5 (5년제) · 7 (설계 7학기)", "6 (툴) · 1 (인턴)"], ["✓ 사실", "넣을지 선택"]),
    ("5", ["ABOUT 카드", "헤드라인 + 2단 본문", "오른쪽 사진"], ["자기소개서 제목을 헤드라인으로", "PROFILE: 학과 · 휴학 · 전향", "INTERESTS: 패션 · 갤러리 · 가구 ·", "조명 · 마감재", "PHOTO 02"], ["사진 ____", "INTERESTS 넣을지"]),
    ("6", ["OUR ADVANTAGES"], ["EDUCATION & EXPERIENCE"], ["문구 선택"]),
    ("7", ["사진 · 카드 체커보드", "카드 오른쪽 EXPLORE"], ["EDUCATION · EXPERIENCE ·", "SKILLS · CONTACT 카드", "EXPLORE 자리 → 기간 · 툴 수", "PHOTO 03 · 04"], ["학교명 · 기간 ____", "사무소명 ____", "연락처 · 어학 ____"]),
]
y += 5.6
for n, ref, cv, st in MAP:
    tag(cols[0] + 2.3, y - 0.9, n, 2.1)
    lh = 2.75
    for j, s in enumerate(ref):
        t(cols[1], y + j * lh, s, 5.4, INK, 400, fam=KR)
    for j, s in enumerate(cv):
        t(cols[2], y + j * lh, s, 5.4, INK, 400, fam=KR)
    for j, s in enumerate(st):
        t(cols[3], y + j * lh, s, 5.4, INK2 if "✓" in s else "#9A4A3A", 500, fam=KR)
    y += max(len(ref), len(cv), len(st)) * lh + 2.6
    ln(MX, y - 2.2, MX + 108, y - 2.2, RULE, 0.2)

# CV factor coverage (from content-reference analysis)
y += 3
t(MX, y, "CV 항목 → 자리", 7, INK, 700, fam=KR)
t(MX + 25, y, "내용 레퍼런스 5장 분석에서 나온 항목이 모두 들어갈 자리", 5.4, INK2, 400, fam=KR)
y += 4.6
COVER = [("이름 · 직무", "1  2", "✓"), ("사진", "2  5  7", "____"), ("소개 · 프로필", "2  5", "✓ 문장 퇴고 중"),
         ("학력", "7 EDUCATION", "학교명 · 연도 ____"), ("경력", "7 EXPERIENCE", "사무소명 · 기간 ____"),
         ("학업 (설계 7학기)", "3  4", "✓"), ("툴 스킬", "7 SKILLS", "✓ 6종"), ("소프트 스킬", "3 강점 카드", "✓"),
         ("연락처", "1 버튼 · 7 CONTACT", "____"), ("어학", "7 SKILLS 끝 줄", "____"), ("수상 · 전시 · 자격증", "있으면 7 EXPERIENCE", "____")]
for name, where, st in COVER:
    t(MX, y, name, 5.4, INK, 500, fam=KR)
    t(MX + 30, y, where, 5.4, INK, 400, fam=KR)
    t(MX + 70, y, st, 5.4, INK2 if st.startswith("✓") else "#9A4A3A", 500, fam=KR)
    y += 3.1
ln(MX, y - 1.6, MX + 108, y - 1.6, RULE, 0.2)

# ---------------------------------------------------------------- right column: title block, types, tone, decisions
RX = 353
ln(RX - 4, 10, RX - 4, 287, INK, 0.3)
r(RX, 10, 58, 50, stroke=INK, sw=0.3)
t(RX + 3, 17.5, "CV", 15, INK, 700)
t(RX + 3, 23.5, "JEONG HYEOKJU", 8, INK, 600, ls=0.3)
t(RX + 3, 27.6, "공간 설계 디자이너 지원 · Gentle Monster", 5.4, INK2, 400, fam=KR)
dl = [("SHEET", "A-01  CV 1/2 레이아웃 청사진"), ("PAGE", "A4 210 × 297 세로 · PDF 2장 중 1장"),
      ("SCALE", "86 % (본문 크기는 실제 pt)"), ("REF", "디자인 ① DVSY · 카드 그리드형"),
      ("DATE", "2026-10-09"), ("STATUS", "청사진 · ____ 칸은 혁주님이 채움"), ("TOOL", "Inkscape 1.2 · SVG → PDF")]
for i, (k, v) in enumerate(dl):
    t(RX + 3, 33 + i * 3.6, k, 4.8, INK2, 600, ls=0.3)
    t(RX + 15, 33 + i * 3.6, v, 5.2, INK, 400, fam=KR)

# 4 reference types as schematics
y0 = 68
t(RX, y0, "DESIGN REFERENCE · 4 TYPES", 7, INK, 700, ls=0.2)
tw, th = 12.5, 22
def thumb(i, draw, name, kind, chosen=False):
    x = RX + i * (tw + 2.6)
    r(x, y0 + 3, tw, th, "#111111" if True else None, INK if chosen else "none", 0.6 if chosen else 0)
    draw(x, y0 + 3)
    t(x, y0 + th + 6.5, name, 4.8, INK, 700)
    for j, s in enumerate(kind):
        t(x, y0 + th + 9.3 + j * 2.4, s, 4.4, INK2, 400, fam=KR)
g = "#5A5A5A"; gl = "#8A8A8A"
def d1(x, y):
    r(x + .8, y + .8, tw - 1.6, .8, g); r(x + .8, y + 2, tw - 1.6, 5, gl)
    for k in range(4): r(x + .8 + k * 2.8, y + 7.5, 2.4, 2, g)
    for k in range(4): r(x + .8 + k * 2.8, y + 10, 2, .5, gl)
    r(x + .8, y + 11, 5.2, 4, g); r(x + 6.5, y + 11, 5.2, 4, gl)
    r(x + .8, y + 15.6, 5.2, 2.8, gl); r(x + 6.5, y + 15.6, 5.2, 1.3, g); r(x + 6.5, y + 17.1, 5.2, 1.3, g)
    r(x + .8, y + 18.8, 5.2, 1.3, g); r(x + .8, y + 20.3, 5.2, 1.3, g); r(x + 6.5, y + 18.8, 5.2, 2.8, gl)
def d2(x, y):
    r(x + .8, y + .8, tw - 1.6, 6, gl); r(x + 1.2, y + 4, 5, 1, "#DDDDDD"); r(x + 1.2, y + 5.4, 5, 1, "#DDDDDD")
    r(x + .8, y + 8, 3, 3.5, gl); r(x + 4.4, y + 8.3, 7, .5, g); r(x + 4.4, y + 9.3, 7, .5, g)
    for k in range(5): r(x + .8 + k * 2.2, y + 12.5, 1.9, 3, gl)
    r(x + .8, y + 17, 3.5, 2.5, gl)
    for k in range(4): r(x + 5, y + 16.6 + k * .9, 6.6, .35, g)
    r(x + 6.5, y + 20.5, 5, .5, g)
def d3(x, y):
    r(x + .8, y + .8, tw - 1.6, 9, "#5A2A28")
    r(x + 1, y + 4, 6, 2.2, "#EEEEEE"); r(x + 5.5, y + 7, 6, 2.2, "#EEEEEE")
    for k in range(4): ln(x + .8 + k * 2.75, y + .8, x + .8 + k * 2.75, y + th - .8, "#444", 0.1)
    for k in range(4): r(x + .8 + k * 2.75, y + 11, 2.3, .5, g)
    for k in range(5): r(x + .8, y + 13 + k * 1.2, 6, .7, g)
    r(x + 8.5, y + 13, 3.2, 4, "#5A2A28")
def d4(x, y):
    r(x + .8, y + .8, tw - 1.6, 6, gl); r(x + 3.5, y + 3.3, 5.5, 1, "#EEEEEE")
    r(x + .8, y + 8.5, 4, .9, g)
    for k in range(4): ln(x + 6, y + 8.5 + k * 1.3, x + tw - .8, y + 8.5 + k * 1.3, g, 0.2)
    r(x + .8, y + 14, 4.5, 4, gl)
    for k in range(4): r(x + 5.6 + k * 1.55, y + 14, 1.35, 4, g)
    for k in range(3): r(x + 5.6 + k * 2.1, y + 19.3, 1.8, .5, g)
    r(x + .8, y + 19.3, 4, .9, g)
thumb(0, d1, "① DVSY", ["카드 그리드형", "선택"], True)
thumb(1, d2, "② ETHAN", ["원페이지", "포트폴리오형"])
thumb(2, d3, "③ ELIAN", ["그리드 ·", "대형 타이포형"])
thumb(3, d4, "④ SONORA", ["에디토리얼", "2단 · 번호 목록"])
y = y0 + th + 18
t(RX, y, "네 장의 공통 문법", 5.6, INK, 700, fam=KR)
lines(RX, y + 3.2, ["검정 바탕 · 흑백 또는 저채도 사진", "영문 대문자 제목 + 아주 작은 본문",
                    "구획은 카드(①) · 가는 선(②④) · 격자(③)", "첫 화면 = 사진 위 대형 이름 또는 제목"], 5.2, 1.3, fill=INK, fam=KR)

# type + tone
y += 19
t(RX, y, "TYPE", 7, INK, 700, ls=0.2)
spec = [("이름", "Inter Thin 51pt · 자간 +3%"), ("섹션 제목", "Inter Light 14pt"), ("카드 제목", "Inter SemiBold 6pt · 대문자"),
        ("본문", "Noto Sans KR 5–5.6pt · 회색"), ("ABOUT 헤드라인", "Noto Sans KR Light 11pt")]
for i, (k, v) in enumerate(spec):
    t(RX, y + 4 + i * 3, k, 5.2, INK2, 500, fam=KR); t(RX + 19, y + 4 + i * 3, v, 5.2, INK, 400, fam=KR)
y += 22
t(RX, y, "TONE", 7, INK, 700, ls=0.2)
sw = [(BG, "바탕", "#0B0B0B"), (CARD, "카드", "#1E1E1E"), (TEXT, "글자", "#ECE8E1"), (SUB, "본문", "#8E8B86")]
for i, (c, k, hx) in enumerate(sw):
    x = RX + i * 14.5
    r(x, y + 2.5, 13, 6, c, INK, 0.15)
    t(x, y + 11.3, k, 4.8, INK, 500, fam=KR); t(x, y + 13.8, hx, 4.4, INK2, 400)
y += 18
t(RX, y, "강조색 후보 (빗금 자리)", 5.4, INK, 700, fam=KR)
acc = [("#D9705C", "레퍼런스 코랄"), ("#445162", "SECTOR A 청회색"), ("#C4B29B", "SECTOR A 베이지")]
for i, (c, k) in enumerate(acc):
    x = RX + i * 19.5
    r(x, y + 2.2, 18, 4.5, c, INK, 0.15, 1)
    t(x, y + 9.4, k, 4.6, INK, 500, fam=KR); t(x, y + 11.8, c, 4.4, INK2, 400)

# open decisions
y += 19
t(RX, y, "혁주님이 정할 것", 7, INK, 700, fam=KR)
dec = ["1  강조색: 코랄 · 청회색 · 베이지 · 그 밖", "2  사진 4장(01–04)을 그대로 둘지, 줄일지", "3  본문 언어: 국문 · 영문 · 국영 병기",
       "4  ④ 숫자 줄을 넣을지", "5  ⑤ INTERESTS 칸을 넣을지", "6  ____ 칸의 사실: 학교명 · 연도 · 사무소명 ·", "    기간 · 연락처 · 어학 · 수상"]
lines(RX, y + 4, dec, 5.3, 1.45, fill=INK, fam=KR)

w('</svg>')
p = Path(__file__).with_name("cv_blueprint.svg")
p.write_text("\n".join(out), encoding="utf-8")
print(p)
