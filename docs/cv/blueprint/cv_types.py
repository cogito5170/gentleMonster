"""CV 1/2 — five layout types drawn from the proportions and copy of the four homepage references.

    python3 docs/cv/blueprint/cv_types.py        # writes types/B-0*.svg and cv_types.pdf (Inkscape + pdfunite)

Sheet B-00 measures the references and sets the A4 translation rules; B-01..B-05 are one type each.
Copy comes only from the applicant's own manuscripts (cover letter Q2, context hand-off). ____ = to be filled.
"""
import subprocess
from pathlib import Path

from bp import *  # noqa: F401,F403  (drawing kit)
import bp

HERE = Path(__file__).parent
TYP = HERE / "types"

# ------------------------------------------------------------------ copy (facts only)
JOB = "SPATIAL DESIGNER  ·  공간 설계 디자이너"
IDENT = "건물을 설계하던 감각으로 매장을 설계하려는 건축학도"  # identity line, still being revised
TITLE_KO = ("틀을 배우고,", "그 안을 채우는 건축학도")  # cover letter Q2 title
STATEMENT = "건축에서 익힌 절제 위에 과감을 더해, 절제와 과감을 한 공간에서 함께 다루고자 합니다."  # Q2, verbatim
PROFILE = ["5년제 건축학과 · 4학년 2학기 휴학", "건축사사무소 인턴을 거쳐", "공간 디자인으로 전향"]
INTERESTS = ["패션 · 갤러리", "가구와 조명 수집", "건축물의 실내 마감재와 마감 방식"]
STRENGTHS = [("01", "PLANNING", "기획", "리서치·분석으로 컨셉을 세우고 건물로 발전시킨 설계 7학기"),
             ("02", "MAKING · TELLING", "구현과 소통", "2D 도면 → 3D 모델링 → 시각화 → 후보정"),
             ("03", "SENSE", "디자인 감각", "시선을 끄는 색과 한발 물러서는 색"),
             ("04", "RESTRAINT + BOLD", "절제와 과감", "건축에서 익힌 절제 위에 과감을 더한다")]
EDU = ["____대학교 건축학과 (5년제)", "4학년 2학기 휴학 중"]
EXP = ["건축사사무소 ____ · 인턴", "현장 실측 · 모델링 · 주변 대지와 프로젝트 건물 구현"]
CONTACT = ["T  ____", "E  ____", "PORTFOLIO  ____"]


def nav_pills(y=8.8, right=203, items=("CONTACT", "SKILLS", "EXPERIENCE", "EDUCATION", "ABOUT")):
    x = right
    for i, p in enumerate(items):
        pw = len(p) * 1.55 + 4.4
        x -= pw
        if i == 0:
            hatch_pill(x, y, pw, 4.6, p)
        else:
            r(x, y, pw, 4.6, "card", rx=0.8)
            t(x + pw / 2, y + 3.1, p, 4.6, "text", 600, "middle", ls=0.2)
        x -= 1.4


# ================================================================== TYPE 1 · CARD GRID (ref 1)
def type1():
    M, CW, G = 7, 196, 2.5
    hw = (CW - G) / 2
    r(0, 0, 210, 297, "bg")
    t(M + 1, 12.6, "JEONG HYEOKJU", 7, "text", 600, ls=0.35)
    nav_pills()
    photo(M, 17, CW, 95, "PHOTO 01", "인물 사진 ____ (흑백 또는 저채도)", rx=1.6, at=(168, 28))
    t(15, 72, "JEONG", 51, "text", 100, ls=1.6)
    t(15, 91, "HYEOKJU", 51, "text", 100, ls=1.6)
    t(16, 99.5, JOB, 6.4, "text", 500, ls=0.2)
    t(16, 103.6, IDENT, 5.6, "sub", 400, fam=KR)
    arrow(170, 102.5, "PAGE 2 · 자기소개서")
    cw = (CW - 3 * G) / 4
    for i, (n, en, ko, d) in enumerate(STRENGTHS):
        x = M + i * (cw + G)
        r(x, 114.5, cw, 26, "card", rx=1.6)
        t(x + 3.5, 120, f"{n}  {en}", 5.6, "text", 600, ls=0.2)
        t(x + 3.5, 123.8, ko, 5.2, "sub", 500, fam=KR)
        para(x + 3.5, 128.4, d, cw - 7, 5.0, fill="sub", fam=KR)
        arrow(x + 5.4, 136.4, "P.2", 1.7)
    r(M, 143, hw, 44, "card", rx=1.6)
    t(M + 5, 149.5, "ABOUT", 5, "text", 600, ls=0.3)
    t(M + 5, 158.5, TITLE_KO[0], 12, "text", 400, fam=KR)
    t(M + 5, 164.3, TITLE_KO[1], 12, "text", 400, fam=KR)
    t(M + 5, 172, "PROFILE", 4.8, "text", 600, ls=0.25); lines(M + 5, 175.8, PROFILE, 5.2, fill="sub", fam=KR)
    t(M + 50, 172, "INTERESTS", 4.8, "text", 600, ls=0.25); lines(M + 50, 175.8, INTERESTS, 5.2, fill="sub", fam=KR)
    photo(M + hw + G, 143, hw, 44, "PHOTO 02", "____ (공간 · 마감재 · 오브제)", rx=1.6)
    for k, (title, body, slot) in enumerate((("EDUCATION", EDU, "____ – ____"), ("EXPERIENCE", EXP, "____"))):
        y = 189.5 + k * (44 + G)
        r(M, y, hw, 44, "card", rx=1.6)
        t(M + 5, y + 7, title, 7, "text", 600, ls=0.3)
        yy = M
        for j, s in enumerate(body):
            para(M + 5, y + 13 + j * 4.2, s, hw - 10, 5.8, fill="sub", fam=KR)
        arrow(M + hw - 26, y + 37, slot)
    x2 = M + hw + G
    r(x2, 189.5, hw, 90.5, "card", rx=1.6)
    t(x2 + 5, 196.5, "SKILLS", 7, "text", 600, ls=0.3)
    t(x2 + hw - 5, 196.5, "LANGUAGE  ____", 4.8, "sub", 500, "end", ls=0.15)
    t(x2 + 5, 201, FLOW, 4.4, "sub", 400, ls=0.1)
    for i, tool in enumerate(TOOLS):
        skill_h(x2 + 5 + (i % 2) * 45, 206 + (i // 2) * 24.5, tool, rr=6, name_pt=6, small=5)
    yF = 282.5
    r(M, yF, CW, 290 - yF, "card", rx=1.6)
    t(M + 4, yF + 4.7, "CONTACT", 5.6, "text", 600, ls=0.25)
    for i, s in enumerate(CONTACT):
        t(M + 30 + i * 36, yF + 4.7, s, 5.2, "sub", 400, fam=KR)
    arrow(M + CW - 28, yF + 3.75, "GET IN TOUCH", 1.7)


# ================================================================== TYPE 2 · SIDEBAR (ref 4 split + content refs)
def type2():
    r(0, 0, 210, 297, "bg")
    r(0, 0, 80, 297, "side")
    photo(0, 0, 80, 112, "PHOTO 01", "인물 사진 ____ (세로 5:7)")
    t(8, 128, "JEONG", 30, "text", 200, ls=0.8)
    t(8, 139.5, "HYEOKJU", 30, "text", 200, ls=0.8)
    t(8, 146.5, "SPATIAL DESIGNER", 5.8, "text", 600, ls=0.3)
    t(8, 150.3, "공간 설계 디자이너 지원", 5.4, "sub", 400, fam=KR)
    para(8, 156, IDENT, 62, 5.2, fill="sub", fam=KR)
    menu = ["01  ABOUT", "02  WHAT I BRING", "03  EDUCATION · EXPERIENCE", "04  SKILLS", "05  COVER LETTER  →  P.2"]
    for i, s in enumerate(menu):
        y = 172 + i * 7
        ln(8, y, 72, y, "line", 0.2)
        t(8, y + 4.6, s, 5.4, "text" if i == 0 else "sub", 600 if i == 0 else 500, ls=0.2)
    ln(8, 207, 72, 207, "line", 0.2)
    t(8, 258, "CONTACT", 5.6, "text", 600, ls=0.3)
    lines(8, 263.5, CONTACT + ["LANGUAGE  ____"], 5.4, 1.6, fill="sub", fam=KR)
    arrow(10, 285, "GET IN TOUCH", 1.8)
    X, RW = 90, 110

    def sec(y, label, right=""):
        ln(X, y, X + RW, y, "line", 0.25)
        t(X, y + 5, label, 5, "sub", 600, ls=0.35)
        if right:
            t(X + RW, y + 5, right, 4.8, "sub", 500, "end", ls=0.15)
    sec(12, "ABOUT")
    t(X, 27, TITLE_KO[0], 15, "text", 400, fam=KR)
    t(X, 34.5, TITLE_KO[1], 15, "text", 400, fam=KR)
    t(X, 44, "PROFILE", 4.8, "text", 600, ls=0.25); lines(X, 48, PROFILE, 5.4, fill="sub", fam=KR)
    t(X + 55, 44, "INTERESTS", 4.8, "text", 600, ls=0.25); lines(X + 55, 48, INTERESTS, 5.4, fill="sub", fam=KR)
    sec(66, "WHAT I BRING  ·  강점")
    for i, (n, en, ko, d) in enumerate(STRENGTHS):
        y = 75 + i * 9.4
        t(X, y + 3.4, n, 6, "sub", 400)
        t(X + 9, y + 3.4, f"{en}  ·  {ko}", 6.2, "text", 600, fam=KR, ls=0.1)
        t(X + 9, y + 7, d, 5.2, "sub", 400, fam=KR)
        ln(X, y + 9, X + RW, y + 9, "line", 0.15)
    sec(118, "EDUCATION  ·  EXPERIENCE")
    for k, (title, body, per) in enumerate((("EDUCATION", EDU, "____ – ____"), ("EXPERIENCE", EXP, "____"))):
        y = 127 + k * 17
        t(X, y + 3, per, 5.4, "sub", 500)
        t(X + 28, y + 3, title, 6.2, "text", 600, ls=0.2)
        for j, s in enumerate(body):
            para(X + 28, y + 7 + j * 3.4, s, RW - 28, 5.4, fill="sub", fam=KR)
    sec(166, "SKILLS", "LANGUAGE  ____")
    t(X, 175.5, FLOW, 4.4, "sub", 400, ls=0.1)
    for i, tool in enumerate(TOOLS):
        skill_h(X + (i % 3) * 37, 180 + (i // 3) * 15.5, tool, rr=4.4, name_pt=5.6, small=4.6, line="____")
    sec(214, "NUMBERS")
    for i, (lab, n, ko) in enumerate((("B.ARCH", "5", "5년제"), ("STUDIOS", "7", "설계 7학기"), ("TOOLS", "6", "2D–편집"), ("INTERN", "1", "건축사사무소"))):
        x = X + i * 27.5
        t(x, 229, n, 16, "text", 200)
        t(x + 6.5, 225.5, lab, 4.6, "sub", 600, ls=0.2); t(x + 6.5, 229, ko, 4.8, "sub", 400, fam=KR)
    ln(X, 262, X + RW, 262, "line", 0.25)
    t(X, 275, "COVER LETTER", 14, "text", 200, ls=0.3)
    t(X, 281.5, "본인 소개와 강점 — 다음 장", 5.4, "sub", 400, fam=KR)
    arrow(X + RW - 22, 276, "PAGE 2", 2.4, 5.4)


# ================================================================== TYPE 3 · SWISS GRID (ref 3)
def type3():
    M, cw = 7, 49
    cols = [M + i * cw for i in range(5)]
    r(0, 0, 210, 297, "bg")
    for x in cols:
        ln(x, 0, x, 297, "grid", 0.2)
    rules = [15, 140, 156, 218, 283.5]
    for y in rules:
        ln(0, y, 210, y, "grid", 0.2)
        for x in cols:
            crosshair(x, y)
    t(cols[0] + 2, 10.5, "JEONG HYEOKJU", 5.4, "text", 700, ls=0.4)
    for i, s in enumerate(("ABOUT", "RECORD", "SKILLS")):
        t(cols[i + 1] + 2, 10.5, s, 5, "sub", 400, fam=MONO, ls=0.3)
    t(cols[4] - 2, 10.5, "CONTACT  →", 5, "text", 600, "end", ls=0.3)
    photo(cols[1], 15, 2 * cw, 125, "PHOTO 01", "인물 사진 ____", at=(cols[2], 28))
    t(cols[0] - 1, 68, "JEONG", 111, "text", 800, ls=-1.2)
    t(cols[4] + 0.5, 131, "HYEOKJU", 111, "text", 800, "end", ls=-1.2)
    lines(cols[4] - 2, 78, ["SPATIAL DESIGNER", "공간 설계 디자이너 지원"], 5.2, 1.5, fill="text", fam=MONO, anchor="end")
    r(cols[0], 128, cw, 12, "bg"); ln(cols[0], 128, cols[1], 128, "grid", 0.2)
    arrow(cols[0] + 4, 134, "PAGE 2 · 자기소개서", 1.8, 4.8)
    info = [("MAJOR", "건축학 · 5년제"), ("STATUS", "4학년 2학기 휴학"), ("APPROACH", "절제 위에 과감"), ("APPLYING FOR", "공간 설계 디자이너")]
    for i, (k, v) in enumerate(info):
        t(cols[i] + 2, 145.5, k, 4.6, "sub", 400, fam=MONO, ls=0.3)
        t(cols[i] + 2, 151.5, v, 6, "text", 400, fam=KR)
    t(cols[0] + 2, 163, "•  ABOUT", 4.8, "sub", 400, fam=MONO, ls=0.3)
    para(cols[0] + 2, 172, STATEMENT, 3 * cw - 8, 15, 1.35, fill="sub", fam=KR, weight=700)
    t(cols[0] + 2, 201, TITLE_KO[0] + " " + TITLE_KO[1], 6.4, "text", 400, fam=KR)
    t(cols[0] + 2, 210, "01 기획   02 구현과 소통   03 디자인 감각   04 절제와 과감", 5.2, "sub", 400, fam=MONO)
    photo(cols[3] + 3, 160, cw - 6, 44, "PHOTO 02", "____")
    lines(cols[4] - 3, 209, ["패션 · 갤러리 · 가구 · 조명", "실내 마감재와 마감 방식"], 4.6, 1.5, fill="sub", fam=MONO, anchor="end")
    for i, (title, body, per) in enumerate((("EDUCATION", EDU, "____ – ____"), ("EXPERIENCE", EXP, "____"))):
        x = cols[i] + 2
        t(x, 224, title, 4.8, "sub", 400, fam=MONO, ls=0.3)
        t(x, 230, per, 6, "text", 400)
        yy = 236
        for s in body:
            yy = para(x, yy, s, cw - 6, 5.4, fill="sub", fam=KR) + 0.8
    t(cols[2] + 2, 224, "SKILLS", 4.8, "sub", 400, fam=MONO, ls=0.3)
    t(cols[4] - 2, 224, "LANGUAGE ____", 4.6, "sub", 400, "end", fam=MONO)
    for i, tool in enumerate(TOOLS):
        skill_h(cols[2] + 2 + (i % 2) * cw, 228 + (i // 2) * 18.5, tool, rr=4.6, name_pt=5.8, small=4.8, line="____")
    for i, s in enumerate(CONTACT + ["GET IN TOUCH  →"]):
        t(cols[i] + 2, 289.5, s, 5, "text" if i == 3 else "sub", 400, fam=MONO)


# ================================================================== TYPE 4 · ONE PAGE (ref 2)
def type4():
    M = 9
    r(0, 0, 210, 297, "bg")
    t(M, 10.5, "JH", 7, "text", 300, ls=0.5)
    for i, s in enumerate(("ABOUT", "SKILLS", "RECORD", "CONTACT")):
        t(201 - (3 - i) * 15, 10.5, s, 4.6, "sub", 500, "end", ls=0.3)
    photo(0, 14, 210, 118, "PHOTO 01", "인물 사진 ____ (흑백)", at=(150, 30))
    t(M, 102, "JEONG", 60, "text", 300, ls=0.2)
    t(M, 124, "HYEOKJU", 60, "text", 300, ls=0.2)
    lines(150, 106, ["SPATIAL DESIGNER", "공간 설계 디자이너 지원"], 5.2, 1.5, fill="text", fam=KR)
    para(150, 114, IDENT, 50, 5, fill="sub", fam=KR)
    t(150, 126.5, "SEE PORTFOLIO", 4.8, "text", 600, ls=0.3); ln(150, 127.3, 168, 127.3, "text", 0.2)
    t(176, 126.5, "PAGE 2", 4.8, "text", 600, ls=0.3); ln(176, 127.3, 185.5, 127.3, "text", 0.2)

    def big(y, s):
        t(M, y, s, 18, "text", 300, ls=0.3)
    big(150, "ABOUT")
    photo(M, 156, 30, 36, "PHOTO 02", "____")
    t(46, 159, "PROFILE", 4.8, "text", 600, ls=0.25); lines(46, 163, PROFILE, 5.4, fill="sub", fam=KR)
    t(120, 159, "INTERESTS", 4.8, "text", 600, ls=0.25); lines(120, 163, INTERESTS, 5.4, fill="sub", fam=KR)
    t(46, 181, TITLE_KO[0], 13, "text", 400, fam=KR); t(46, 187.5, TITLE_KO[1], 13, "text", 400, fam=KR)
    big(205, "SKILLS")
    t(201, 205, FLOW, 4.4, "sub", 400, "end", ls=0.1)
    tw = (192 - 5 * 1.5) / 6
    for i, tool in enumerate(TOOLS):
        x = M + i * (tw + 1.5)
        r(x, 209, tw, 28, "card")
        skill_v(x, 211.5, tw, tool, rr=5)
    t(201, 241.5, "LANGUAGE  ____", 4.6, "sub", 500, "end", ls=0.15)
    big(254, "RECORD")
    photo(M, 258, 62, 24, "PHOTO 03", "____ (작업 이미지)")
    rows = [("01.", "EDUCATION", EDU[0] + " · " + EDU[1], "____ – ____"),
            ("02.", "EXPERIENCE", EXP[0], "____"),
            ("03.", "DESIGN STUDIOS", "설계 수업 7학기 · 1학년부터 매 학기", ""),
            ("04.", "WHAT I BRING", "기획 · 구현과 소통 · 디자인 감각 · 절제와 과감", "→ P.2")]
    for i, (n, ttl, d, per) in enumerate(rows):
        y = 247 + i * 9.4
        t(80, y + 3.6, f"{n} {ttl}", 6, "text", 600, ls=0.2)
        t(201, y + 3.6, per, 5, "sub", 500, "end")
        t(80, y + 7.1, d, 5.2, "sub", 400, fam=KR)
        ln(80, y + 8.8, 201, y + 8.8, "line", 0.15)
    t(105, 290.5, "JEONG HYEOKJU", 6.4, "text", 400, "middle", ls=0.4)
    t(105, 294, "T ____   ·   E ____   ·   PORTFOLIO ____", 4.6, "sub", 400, "middle", fam=KR)


# ================================================================== TYPE 5 · EDITORIAL INDEX (ref 4), light
def type5():
    M, L, X = 10, 72, 88
    RW = 200 - X
    r(0, 0, 210, 297, "bg")
    t(M, 10.8, "Jeong Hyeokju", 7.4, "text", 500)
    for i, s in enumerate(("ABOUT", "RECORD", "TOOLS", "CONTACT")):
        t(200 - (3 - i) * 15, 10.8, s, 4.6, "text", 600, "end", ls=0.3)
    photo(0, 15, 210, 95, "PHOTO 01", "인물 사진 ____ (흑백)", at=(105, 30))
    t(105, 70, "JEONG HYEOKJU", 30, "#F2EFE9", 500, "middle", ls=0.6)
    t(105, 78, JOB, 6, "#F2EFE9", 500, "middle", ls=0.3)

    def row(y, h1, h2=""):
        ln(M, y, 200, y, "text", 0.25)
        t(M, y + 8, h1, 12, "text", 500, fam=KR)
        if h2:
            t(M, y + 13.5, h2, 12, "text", 500, fam=KR)
    row(118, TITLE_KO[0], TITLE_KO[1])
    para(X, 124, IDENT, RW, 6.2, fill="text", fam=KR)
    t(X, 133, "PROFILE", 4.8, "text", 600, ls=0.25); lines(X, 137, PROFILE, 5.6, fill="sub", fam=KR)
    t(X + 56, 133, "INTERESTS", 4.8, "text", 600, ls=0.25); lines(X + 56, 137, INTERESTS, 5.6, fill="sub", fam=KR)
    row(160, "WHAT I BRING")
    for i, (n, en, ko, d) in enumerate(STRENGTHS):
        y = 160 + i * 11.4
        t(X, y + 5.4, n, 6.4, "text", 500)
        t(X + 10, y + 5.4, f"{ko}  {en}", 6.4, "text", 600, fam=KR, ls=0.1)
        t(X + 10, y + 9.4, d, 5.4, "sub", 400, fam=KR)
        if i < 3:
            ln(X, y + 11.4, 200, y + 11.4, "line", 0.2)
    row(210, "EDUCATION", "EXPERIENCE")
    for k, (title, body, per) in enumerate((("EDUCATION", EDU, "____ – ____"), ("EXPERIENCE", EXP, "____"))):
        y = 214 + k * 13
        t(X, y + 3, per, 5.6, "sub", 500)
        t(X + 26, y + 3, title, 6.2, "text", 600, ls=0.2)
        t(X + 26, y + 6.8, body[0], 5.4, "sub", 400, fam=KR)
        t(X + 26, y + 10.2, body[1], 5.4, "sub", 400, fam=KR)
    row(244, "TOOLS")
    t(M, 263, "LANGUAGE  ____", 5, "sub", 500, ls=0.15)
    t(M, 268, FLOW.replace(" → ", " → "), 4.2, "sub", 400)
    for i, tool in enumerate(TOOLS):
        skill_h(X + (i % 3) * 37.5, 248 + (i // 3) * 16, tool, rr=4.4, name_pt=5.8, small=4.8, line="____")
    ln(M, 283, 200, 283, "text", 0.25)
    arrow(M + 2, 288.6, "PAGE 2 · 자기소개서", 1.8, 5)
    for i, s in enumerate(CONTACT):
        t(X + i * 38, 289.6, s, 5.2, "text", 400, fam=KR)


# ================================================================== sheet specs
TYPES = [
    dict(code="B-01", fn=type1, th=DARK, en="CARD GRID", ko="카드 그리드", ref="①  DVSY", pos=3, photos=2,
         zones=[("1", "NAV", 7, 15), ("2", "HERO", 17, 112), ("3", "CARDS ×4", 114.5, 140.5), ("4", "ABOUT", 143, 187),
                ("5", "GRID", 189.5, 280), ("6", "FOOTER", 282.5, 290)],
         xs=[0, 7, 103.75, 106.25, 203, 210], note="여백 7 · 사이 2.5 (폭의 1.2 %) · 반폭 96.75 · 모서리 R1.6",
         prop=[("첫 화면", "95 = 폭 × 0.48", "① 0.49"), ("이름 대문자 높이", "13 = 폭의 6.3 % (51pt Thin)", "① 6.3 %"),
               ("열", "2열 반반 · 강점은 4열", "① 2열 · 4열"), ("사이", "2.5 = 폭의 1.2 %", "① 1.1 %"),
               ("제목 : 본문", "51 : 5.6pt ≈ 9 : 1", "① 약 6–9 : 1"), ("구획", "둥근 카드 R1.6", "① 카드")],
         text=[("이름", "얇은 대문자 두 줄", "① DESIGN & FREEDOM"), ("카드", "영문 대문자 제목 + 국문 한 줄 + 링크", "① 제목 · 두 줄 · LEARN MORE"),
               ("ABOUT", "자기소개서 제목이 헤드라인", "① WHERE FASHION MEETS FREEDOM"), ("링크", "P.2 · GET IN TOUCH", "① EXPLORE")],
         fit=["레퍼런스 ①을 가장 가깝게 따름", "강점 4개가 첫 화면 바로 아래에서 보임", "툴 링 배지가 다섯 안 중 가장 큼 (Ø12)"],
         care=["카드가 많아 정보의 위계가 평평해질 수 있음", "rev.B 보다 숫자 줄과 PHOTO 03 · 04를 뺌"],
         ask=["숫자 줄을 뺀 것이 괜찮은지", "ABOUT 오른쪽 사진의 내용 ____"]),
    dict(code="B-02", fn=type2, th=DARK, en="SIDEBAR", ko="고정 사이드바", ref="④ 2단 + 내용 레퍼런스 ①②④", pos=2, photos=1,
         zones=[("1", "ABOUT", 12, 62), ("2", "STRENGTHS", 66, 112), ("3", "RECORD", 118, 160), ("4", "SKILLS", 166, 210),
                ("5", "NUMBERS", 214, 240), ("6", "NEXT", 262, 285)],
         xs=[0, 80, 90, 200, 210], note="사이드바 80 : 본문 130 = 38 : 62 · 오른쪽 구역 치수는 본문 열 기준",
         prop=[("좌우 나눔", "80 : 130 = 38 : 62", "④ 제목 38 : 내용 62"), ("사이드바 사진", "80 × 112 = 5 : 7 세로", "내용 레퍼런스 ①②④ 세로 인물"),
               ("이름", "30pt ExtraLight (폭의 3.6 %)", "첫 화면 대신 사이드바가 이름을 맡음"), ("행 구분", "가는 선 0.2 · 행 높이 9.4", "④ 가는 선"),
               ("제목 : 본문", "15 : 5.4pt ≈ 3 : 1", "④ 약 4 : 1"), ("구획", "선만 · 카드 없음", "④")],
         text=[("메뉴", "세로 목차 01–05", "홈페이지 메뉴를 세로로"), ("섹션", "작은 대문자 라벨 + 번호 목록", "④ 01 Touchup"),
               ("강점", "번호 · 영문 · 국문 · 한 줄", "④ 번호 + 이름 + 설명"), ("마지막", "COVER LETTER → PAGE 2", "① LEARN MORE")],
         fit=["사진 1장이면 됨", "이름 · 연락처가 한쪽에 고정되어 읽는 순서가 분명", "내용 레퍼런스의 2단 CV와 가장 가까워 서류로 익숙함"],
         care=["홈페이지 느낌은 ①보다 약함", "사이드바 아래쪽(207–255)이 비어 숨 쉬는 자리 — 채울지 정해야 함"],
         ask=["사이드바 빈자리를 둘지, 채울지"]),
    dict(code="B-03", fn=type3, th=DARK, en="SWISS GRID", ko="격자 · 대형 타이포", ref="③  ELIAN KENT", pos=5, photos=2,
         zones=[("1", "TOP", 7, 15), ("2", "HERO", 15, 140), ("3", "INFO", 140, 156), ("4", "ABOUT", 156, 218),
                ("5", "GRID", 218, 283.5), ("6", "FOOT", 283.5, 290)],
         xs=[0, 7, 56, 105, 154, 203, 210], note="4열 × 49 · 격자선과 교점 십자 표시가 그대로 보임",
         prop=[("열", "4열 × 49 (각 23 %)", "③ 4열 각 24 %"), ("첫 화면", "125 = 폭 × 0.60", "③ 0.70 → A4 세로라 줄임"),
               ("이름 대문자 높이", "29 = 폭의 13.6 % (111pt ExtraBold)", "③ 13.6 %"), ("이름 배치", "JEONG 왼쪽 위 · HYEOKJU 오른쪽 아래", "③ ELIAN / KENT 엇갈림"),
               ("제목 : 본문", "111 : 5.4pt ≈ 20 : 1", "③ 약 20 : 1"), ("구획", "격자선 + 십자", "③")],
         text=[("정보 줄", "MAJOR · STATUS · APPROACH · APPLYING FOR", "③ LOCATION · FIELD · APPROACH · CLIENTS"),
               ("APPROACH", "절제 위에 과감", "③ LESS BUT BETTER"),
               ("소개", "자기소개서 문장 그대로, 큰 회색 글자", "③ I'M A FRAMER DESIGNER …"), ("작은 글", "고정폭 글꼴 (Noto Sans Mono)", "③ 모노 캡션")],
         fit=["가장 과감한 안 — 자기소개서의 '절제 위에 과감'을 지면이 먼저 보여 줌", "격자는 도면의 기준선과 같은 말 — 건축 배경과 이어짐"],
         care=["이름이 지면 위쪽 절반을 차지, 사진이 이름 뒤에 가려짐", "긴 설명을 담기 어려움 — 정보는 짧은 값 위주"],
         ask=["이름을 이 크기로 둘지 (과감의 정도)", "소개 문장을 자기소개서와 같은 문장으로 둘지"]),
    dict(code="B-04", fn=type4, th=DARK, en="ONE PAGE", ko="원페이지 포트폴리오", ref="②  ETHAN CARTER", pos=4, photos=3,
         zones=[("1", "NAV", 6, 13), ("2", "HERO", 14, 132), ("3", "ABOUT", 140, 192), ("4", "SKILLS", 194, 242),
                ("5", "RECORD", 244, 283), ("6", "FOOTER", 286, 295)],
         xs=[0, 9, 201, 210], note="단일 열 · 여백 9 · 스킬 띠 6칸 × 30.75 · 사이 1.5",
         prop=[("첫 화면", "118 = 폭 × 0.56", "② 0.57"), ("이름 대문자 높이", "15.5 = 폭의 7.4 % (60pt Light)", "② 7.4 %"),
               ("섹션 제목", "18pt Light, 왼쪽 정렬", "② ABOUT · WORKS · SERVICES"), ("스킬 띠", "6칸 균등 · 각 30.75 × 28", "② 작업 사진 띠 5칸"),
               ("제목 : 본문", "60 : 5.4pt ≈ 11 : 1", "② 약 10 : 1"), ("여백", "9 = 폭의 4 %", "② 2.7 %")],
         text=[("첫 화면", "이름 + 오른쪽 작은 소개 + 밑줄 링크", "② SEE MY WORK · CONTACT"), ("ABOUT", "사진 + 2단 글 + 큰 문장(자기소개서 제목)", "② READY TO LEAVE YOUR MARK?"),
               ("RECORD", "01. EDUCATION … 번호 목록", "② 01. ARTISTIC TATTOOING"), ("푸터", "이름을 한 번 더 + 연락처", "② 푸터 이름")],
         fit=["위에서 아래로 스크롤하는 홈페이지 느낌이 가장 강함", "툴 6개가 한 줄 띠로 나란히 — 작업 순서가 한눈에 보임"],
         care=["사진 3장이 필요함", "섹션이 많아 아래쪽 여백이 빠듯함 (푸터 여백 2)"],
         ask=["PHOTO 02 · 03에 쓸 사진 ____"]),
    dict(code="B-05", fn=type5, th=LIGHT, en="EDITORIAL INDEX", ko="에디토리얼 목차", ref="④  SONORA", pos=1, photos=1,
         zones=[("1", "NAV", 6, 13), ("2", "HERO", 15, 110), ("3", "ABOUT", 118, 156), ("4", "STRENGTHS", 160, 206),
                ("5", "RECORD", 210, 240), ("6", "TOOLS", 244, 280), ("7", "FOOT", 283, 292)],
         xs=[0, 10, 82, 88, 200, 210], note="왼쪽 제목 72 : 오른쪽 내용 112 ≈ 38 : 62 · 바탕 #E6E2DA",
         prop=[("첫 화면", "95 = 폭 × 0.45", "④ 0.51"), ("왼쪽 제목 : 오른쪽 내용", "72 : 112 ≈ 39 : 61", "④ 38 : 62"),
               ("제목", "이름 30pt Medium 가운데", "④ ABOUT US 가운데"), ("행", "가는 선으로만 구획, 카드 없음", "④"),
               ("제목 : 본문", "12 : 5.6pt ≈ 2 : 1 (본문 쪽이 가장 큼)", "④ 약 3 : 1"), ("바탕", "밝은 회베이지 #E6E2DA", "내용 레퍼런스 ③⑤ 회색 종이 · SECTOR A")],
         text=[("섹션 제목", "문장이 곧 제목: 틀을 배우고, / 그 안을 채우는 건축학도", "④ WE PROVIDE VARIOUS SERVICES"),
               ("강점", "번호 + 국문 · 영문 + 한 줄", "④ 01 Touchup + 설명"), ("로고", "문장형 대소문자 Jeong Hyeokju", "④ Sonora"),
               ("툴", "3열 × 2행", "④ 아래쪽 3열 서비스 격자")],
         fit=["가장 절제된 안 — 검정 · 베이지 · 회색만, 원색 없음 (MY STYLE 색)", "선으로만 나눠 비례가 그대로 드러남", "사진 1장"],
         care=["레퍼런스 ①의 어두운 홈페이지 톤에서 가장 멂", "강조색이 들어갈 자리가 거의 없음"],
         ask=["밝은 바탕으로 갈지, 같은 구성을 어둡게 할지"]),
]

COMMON_ASK = ["다섯 안 중 고를 유형 (섞어도 됨)", "강조색 · 숙련도 링 값 · 툴별 한 줄 ____", "____ 칸의 사실: 학교명 · 연도 · 사무소명 · 기간 · 연락처 · 어학"]

S, OX, OY = 0.86, 24, 26
MX, RX = 237, 353


def type_sheet(spec, n):
    sheet_open()
    t(OX, 13, f"{spec['code']}   TYPE {n} · {spec['en']}", 9, INK, 700, ls=0.3)
    t(OX, 17.6, f"{spec['ko']} — 디자인 레퍼런스 {spec['ref']}의 비례와 글을 A4 세로 CV 1장으로 옮긴 안. 86 % 축척, 치수는 실제 mm.", 6, INK2, 400, fam=KR)
    drawing(spec["fn"], OX, OY, S, spec["th"])
    dims(OX, OY, S, spec["zones"], spec["xs"], spec["note"])
    ln(MX - 4, 10, MX - 4, 287, INK, 0.3)
    y = heading(MX, 15, "PROPORTION", "비례 — 값과 레퍼런스 근거")
    y = table(MX, y + 1, [(0, 24), (24, 46), (70, 38)], spec["prop"], head=["항목", "이 안의 값", "레퍼런스"])
    y = heading(MX, y + 5, "TEXT", "글 — 처리 방식과 근거")
    y = table(MX, y + 1, [(0, 18), (18, 52), (70, 38)], spec["text"], head=["자리", "이 안의 글", "레퍼런스"])
    y = heading(MX, y + 5, "CONTENT", "CV 항목이 놓인 자리")
    place = {
        "B-01": [("강점 4", "3 카드"), ("학력 · 경력", "5 왼쪽 카드 2"), ("툴 6", "5 오른쪽 링 배지 3×2"), ("연락처", "1 버튼 · 6 푸터")],
        "B-02": [("이름 · 사진 · 연락처", "사이드바 (고정)"), ("강점 4", "2 번호 목록"), ("학력 · 경력", "3 기간 | 내용"), ("툴 6", "4 링 배지 3×2"), ("숫자", "5")],
        "B-03": [("학과 · 상태 · 지원", "3 정보 줄"), ("강점 4", "4 한 줄 모노"), ("학력 · 경력", "5 열 1 · 2"), ("툴 6", "5 열 3–4 링 배지"), ("연락처", "6")],
        "B-04": [("소개", "3 사진 + 2단 + 문장"), ("툴 6", "4 띠 6칸"), ("학력 · 경력 · 설계 7학기 · 강점", "5 번호 목록 01–04"), ("연락처", "6 푸터")],
        "B-05": [("소개", "3 문장 제목 | 글"), ("강점 4", "4 번호 목록"), ("학력 · 경력", "5"), ("툴 6", "6 링 배지 3×2"), ("연락처", "7")],
    }[spec["code"]]
    y = table(MX, y + 1, [(0, 40), (40, 68)], place, colors=[INK, INK])
    t(MX, y + 3, "모든 안에 같은 사실만 씀. 모르는 칸은 ____ . 사진 수: " + str(spec["photos"]) + "장.", 5.3, INK2, 400, fam=KR)

    ln(RX - 4, 10, RX - 4, 287, INK, 0.3)
    r(RX, 10, 58, 46, stroke=INK, sw=0.3)
    t(RX + 3, 18, f"TYPE {n}", 14, INK, 700)
    t(RX + 3, 24, spec["en"], 8, INK, 600, ls=0.3)
    t(RX + 3, 28.2, spec["ko"], 5.6, INK2, 400, fam=KR)
    rows = [("SHEET", f"{spec['code']}  ·  6장 중 {n + 1}"), ("PAGE", "CV 1/2 · A4 세로"), ("REF", spec["ref"]),
            ("PHOTOS", f"{spec['photos']}장"), ("DATE", "2026-10-09"), ("TOOL", "Inkscape 1.2 · SVG → PDF")]
    for i, (k, v) in enumerate(rows):
        t(RX + 3, 34 + i * 3.6, k, 4.8, INK2, 600, ls=0.3); t(RX + 16, 34 + i * 3.6, v, 5.2, INK, 400, fam=KR)
    y = heading(RX, 66, "TONE", "절제 ↔ 과감")
    scale_bar(RX + 2, y + 4, 52, spec["pos"])
    y = heading(RX, y + 16, "FIT", "맞는 점")
    for s in spec["fit"]:
        y = para(RX, y + 0.6, "· " + s, 57, 5.3, 1.4, fill=INK, fam=KR) + 0.8
    y = heading(RX, y + 4, "CARE", "주의")
    for s in spec["care"]:
        y = para(RX, y + 0.6, "· " + s, 57, 5.3, 1.4, fill=INK, fam=KR) + 0.8
    y = heading(RX, y + 4, "ASK", "혁주님이 정할 것")
    for s in spec["ask"] + COMMON_ASK:
        y = para(RX, y + 0.6, "· " + s, 57, 5.3, 1.4, fill=RED if "____" in s else INK, fam=KR) + 0.8
    sheet_close(TYP / f"{spec['code']}.svg")


# ================================================================== B-00 overview
def overview():
    sheet_open()
    t(16, 17, "B-00   PROPORTION STUDY  ·  5 TYPES", 10, INK, 700, ls=0.3)
    t(16, 22.5, "디자인 레퍼런스 4장(홈페이지)의 비례와 글을 재서 A4 세로 CV 1장으로 옮기는 규칙, 그리고 그 규칙으로 만든 다섯 안.", 6.2, INK2, 400, fam=KR)
    y = heading(16, 33, "MEASURE", "레퍼런스 측정 — 스크린샷에서 잰 값, 폭 = 1")
    cols = [(0, 30), (30, 40), (70, 40), (110, 40), (150, 40)]
    rows = [("", "① DVSY", "② ETHAN CARTER", "③ ELIAN KENT", "④ SONORA"),
            ("첫 화면 높이", "0.49", "0.57", "0.70", "0.51"),
            ("이름 · 제목 대문자 높이", "6.3 %", "7.4 %", "13.6 %", "4.8 %"),
            ("열 구성", "2열 반반 · 4열 카드", "본문 열 32 % 들여 시작", "4열 균등 (각 24 %)", "제목 38 : 내용 62"),
            ("구획", "둥근 카드 + 사이 1.1 %", "가는 선 · 빈 여백", "격자선 + 교점 십자", "가는 선 · 번호"),
            ("제목 : 본문", "약 6–9 : 1", "약 10 : 1", "약 20 : 1", "약 3 : 1"),
            ("사진", "첫 화면 + 바둑판 2", "첫 화면 + 띠 5 + 1", "첫 화면 + 작은 세로 1", "첫 화면 + 세로 띠 5"),
            ("글", "가치 단어 4 + 한 줄 + LEARN MORE", "질문형 선언 + 번호 목록", "키–값 4칸 + 1인칭 긴 문장", "문장형 섹션 제목 + 01 목록")]
    y = table(16, y + 1, cols, rows, pt=5.6, lh=2.8, colors=[INK] * 5)
    y = heading(16, y + 5, "RULES", "A4로 옮기는 규칙")
    rules = ["1  첫 화면 높이 = 폭 × 0.45–0.60. 웹은 세로로 흐르지만 A4는 297에서 끝나서 ③의 0.70은 0.60으로 줄임.",
             "2  이름 크기는 레퍼런스의 '대문자 높이 / 폭' 비를 그대로 씀: ① 51pt · ② 60pt · ③ 111pt · ④ 30pt.",
             "3  본문은 인쇄 하한 5pt 이상, 5.2–6pt. 제목 : 본문 비는 레퍼런스 비를 따름.",
             "4  열은 레퍼런스의 나눔을 그대로: 반반 · 38 : 62 · 4열.",
             "5  글은 지어내지 않음: 자기소개서 제목 · 강점 · 문장, 받은 사실만. 모르는 칸은 ____ .",
             "6  SKILLS는 다섯 안 모두 링 배지 + 쓰임 + 한 줄 (스킬 레퍼런스 A · B)을 지킴."]
    for s in rules:
        y = para(16, y + 0.8, s, 188, 5.8, 1.4, fill=INK, fam=KR) + 1
    y = heading(16, y + 6, "COPY", "다섯 안에 쓴 글과 출처 — 새로 지은 문장 없음")
    src = [("JEONG HYEOKJU · 공간 설계 디자이너", "맥락 전달 (이름) · 채용 공고 (직무)"),
           ("건물을 설계하던 감각으로 매장을 설계하려는 건축학도", "자기소개서 문항 2 첫 문장 — 퇴고 중"),
           ("틀을 배우고, 그 안을 채우는 건축학도", "자기소개서 문항 2 제목"),
           ("기획 · 구현과 소통 · 디자인 감각 · 절제와 과감", "자기소개서 문항 2 강점 셋 + 마지막 문단"),
           ("건축에서 익힌 절제 위에 과감을 더해, …", "자기소개서 문항 2 마지막 문단 그대로"),
           ("PROFILE: 5년제 · 4학년 2학기 휴학 · 인턴 · 전향", "맥락 전달 1 · 자기소개서 문항 2"),
           ("INTERESTS: 패션 · 갤러리 · 가구와 조명 · 마감재", "맥락 전달 3 (관심사)"),
           ("툴 6 · 숫자 5 · 7 · 6 · 1", "맥락 전달 1 · 자기소개서 문항 2"),
           ("영문 라벨 (ABOUT · WHAT I BRING · RECORD …)", "레퍼런스의 메뉴 · 섹션 이름 방식")]
    y = table(16, y + 1, [(0, 95), (95, 95)], src, pt=5.6, lh=2.8, colors=[INK, INK2])
    # five thumbnails
    th_s, tx0, ty = 0.30, 214, 36
    t(tx0, 33, "FIVE TYPES", 8, INK, 700, ls=0.3)
    t(tx0 + 26, 33, "30 % 축척 · 각 안의 자세한 시트는 B-01–B-05", 5.6, INK2, 400, fam=KR)
    gap = 3
    for i, spec in enumerate(TYPES):
        col, rowi = i % 3, i // 3
        x = tx0 + col * (210 * th_s + gap)
        yy = ty + rowi * (297 * th_s + 14)
        drawing(spec["fn"], x, yy, th_s, spec["th"])
        r(x, yy, 210 * th_s, 297 * th_s, stroke=INK, sw=0.2)
        t(x, yy + 297 * th_s + 4, f"TYPE {i + 1} · {spec['en']}", 5.6, INK, 700, ls=0.2)
        t(x, yy + 297 * th_s + 7.2, f"{spec['ko']} · {spec['ref']}", 5, INK2, 400, fam=KR)
    # tone scale in the 6th slot
    x = tx0 + 2 * (210 * th_s + gap); yy = ty + 297 * th_s + 14
    t(x, yy + 6, "TONE", 8, INK, 700, ls=0.3)
    t(x, yy + 11, "절제 ↔ 과감 — 자기소개서의", 5.6, INK2, 400, fam=KR)
    t(x, yy + 14.4, "'절제 위에 과감'을 어디에 둘지", 5.6, INK2, 400, fam=KR)
    scale_bar(x + 3, yy + 30, 56, 0, marks=[(spec["pos"], str(i + 1)) for i, spec in enumerate(TYPES)])
    order = sorted(range(5), key=lambda i: TYPES[i]["pos"])
    for k, i in enumerate(order):
        sp = TYPES[i]
        t(x, yy + 44 + k * 3.6, f"{sp['pos']}  TYPE {i + 1} · {sp['ko']} · 사진 {sp['photos']}장", 5.4, INK, 400, fam=KR)
    sheet_close(TYP / "B-00.svg")


def main():
    TYP.mkdir(exist_ok=True)
    overview()
    for i, spec in enumerate(TYPES, 1):
        type_sheet(spec, i)
    pdfs = []
    for code in ["B-00"] + [s["code"] for s in TYPES]:
        svg, pdf = TYP / f"{code}.svg", TYP / f"{code}.pdf"
        subprocess.run(["inkscape", str(svg), "--export-type=pdf", f"--export-filename={pdf}"], check=True, capture_output=True)
        pdfs.append(str(pdf))
    subprocess.run(["pdfunite", *pdfs, str(HERE / "cv_types.pdf")], check=True)
    print(HERE / "cv_types.pdf")


if __name__ == "__main__":
    main()
