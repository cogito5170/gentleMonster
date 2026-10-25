"""TYPE 2 (sidebar) re-laid around the smaller photo S (48 x 64).

    python3 docs/cv/blueprint/type2b.py   # -> docs/cv/ai/CV_TYPE2B_SIDEBAR.ai / .svg

What moved, and why:
- sidebar: photo 80 x 112 -> 48 x 64 framed at the 8 mm margin; name, lines and menu move up.
  The freed sidebar height takes the NUMBERS block (2 x 2), so the sidebar holds who-I-am at a glance:
  photo, name, role, menu, numbers, contact.
- right column: NUMBERS leaves it, so ABOUT, strengths and record get more line space and larger
  body type (5.4 -> 5.6 pt), and SKILLS turns into 3 x 2 ring badges (skill ref A) with room to breathe.
Copy is unchanged.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bp  # noqa: E402
from bp import *  # noqa: F401,F403,E402
from cv_types import CONTACT, EDU, EXP, FLOW, IDENT, INTERESTS, PROFILE, STRENGTHS, TITLE_KO, TOOLS  # noqa: E402

AI = Path(__file__).resolve().parent.parent / "ai"
NUMS = (("B.ARCH", "5", "5년제"), ("STUDIOS", "7", "설계 7학기"), ("TOOLS", "6", "2D–편집"), ("INTERN", "1", "건축사사무소"))


def type2b():
    zone("T2B_01_BACKGROUND")
    r(0, 0, 210, 297, "bg")
    zone("T2B_02_SIDEBAR")
    r(0, 0, 80, 297, "side")
    photo(8, 12, 48, 64, "PHOTO 01", "____ (48 × 64)", rx=1.2)
    t(8, 92, "JEONG", 30, "text", 200, ls=0.8)
    t(8, 103.5, "HYEOKJU", 30, "text", 200, ls=0.8)
    t(8, 110.5, "SPATIAL DESIGNER", 5.8, "text", 600, ls=0.3)
    t(8, 114.3, "공간 설계 디자이너 지원", 5.4, "sub", 400, fam=KR)
    para(8, 120, IDENT, 62, 5.2, fill="sub", fam=KR)
    menu = ["01  ABOUT", "02  WHAT I BRING", "03  EDUCATION · EXPERIENCE", "04  SKILLS", "05  COVER LETTER  →  P.2"]
    for i, s in enumerate(menu):
        y = 136 + i * 7
        ln(8, y, 72, y, "line", 0.2)
        t(8, y + 4.6, s, 5.4, "text" if i == 0 else "sub", 600 if i == 0 else 500, ls=0.2)
    ln(8, 171, 72, 171, "line", 0.2)
    t(8, 186, "NUMBERS", 5.6, "text", 600, ls=0.3)
    for i, (lab, n, ko) in enumerate(NUMS):
        x, y = 8 + (i % 2) * 34, 200 + (i // 2) * 19
        t(x, y, n, 20, "text", 200)
        t(x + 8.5, y - 4.4, lab, 4.6, "sub", 600, ls=0.2)
        t(x + 8.5, y - 0.6, ko, 4.8, "sub", 400, fam=KR)
    ln(8, 236, 72, 236, "line", 0.2)
    t(8, 252, "CONTACT", 5.6, "text", 600, ls=0.3)
    lines(8, 257.5, CONTACT + ["LANGUAGE  ____"], 5.4, 1.6, fill="sub", fam=KR)
    arrow(10, 285, "GET IN TOUCH", 1.8)
    X, RW = 90, 110

    def sec(y, label, right=""):
        ln(X, y, X + RW, y, "line", 0.25)
        t(X, y + 5, label, 5, "sub", 600, ls=0.35)
        if right:
            t(X + RW, y + 5, right, 4.8, "sub", 500, "end", ls=0.15)
    zone("T2B_03_ABOUT")
    sec(12, "ABOUT")
    t(X, 27, TITLE_KO[0], 15, "text", 400, fam=KR)
    t(X, 34.5, TITLE_KO[1], 15, "text", 400, fam=KR)
    t(X, 45, "PROFILE", 4.8, "text", 600, ls=0.25); lines(X, 49.2, PROFILE, 5.6, fill="sub", fam=KR)
    t(X + 55, 45, "INTERESTS", 4.8, "text", 600, ls=0.25); lines(X + 55, 49.2, INTERESTS, 5.6, fill="sub", fam=KR)
    zone("T2B_04_STRENGTHS")
    sec(68, "WHAT I BRING  ·  강점")
    for i, (n, en, ko, d) in enumerate(STRENGTHS):
        y = 77 + i * 11.5
        t(X, y + 3.8, n, 6.4, "sub", 400)
        t(X + 9, y + 3.8, f"{en}  ·  {ko}", 6.6, "text", 600, fam=KR, ls=0.1)
        t(X + 9, y + 7.9, d, 5.6, "sub", 400, fam=KR)
        ln(X, y + 11, X + RW, y + 11, "line", 0.15)
    zone("T2B_05_EDUCATION_EXPERIENCE")
    sec(128, "EDUCATION  ·  EXPERIENCE")
    for k, (title, body, per) in enumerate((("EDUCATION", EDU, "____ – ____"), ("EXPERIENCE", EXP, "____"))):
        y = 137 + k * 19
        t(X, y + 3.2, per, 5.6, "sub", 500)
        t(X + 28, y + 3.2, title, 6.6, "text", 600, ls=0.2)
        for j, s in enumerate(body):
            para(X + 28, y + 7.6 + j * 3.6, s, RW - 28, 5.6, fill="sub", fam=KR)
    zone("T2B_06_SKILLS")
    sec(178, "SKILLS", "LANGUAGE  ____")
    t(X, 187.5, FLOW, 4.6, "sub", 400, ls=0.1)
    cw = RW / 3
    for i, tool in enumerate(TOOLS):
        skill_v(X + (i % 3) * cw, 191 + (i // 3) * 28, cw, tool, rr=5.5)
    zone("T2B_07_COVER_LETTER_LINK")
    ln(X, 256, X + RW, 256, "line", 0.25)
    t(X, 272, "COVER LETTER", 14, "text", 200, ls=0.3)
    t(X, 278.5, "본인 소개와 강점 — 다음 장", 5.4, "sub", 400, fam=KR)
    arrow(X + RW - 22, 273, "PAGE 2", 2.4, 5.4)
    zone_end()


# ---- 2C: proportions from the applicant's portfolio (JAJU portfolio, InDesign 315 x 195)
#   part cover /02 Match: left colour band 104.5 / 315 = 1/3  -> sidebar 70 of 210 (was 80 = 38 %)
#   top / bottom guide lines at 11.58 / 195 and 180.5 / 195   -> 17.6 and 275 on A4
#   bottom line (folio) at 184.35 / 195                        -> 280.8
W_SIDE = 210 / 3
TOP, BOT, FOLIO = 297 * 11.58 / 195, 297 * 180.5 / 195, 297 * 184.35 / 195


def type2c():
    S, T = W_SIDE, TOP
    zone("T2C_01_BACKGROUND")
    r(0, 0, 210, 297, "bg")
    zone("T2C_02_SIDEBAR")
    r(0, 0, S, 297, "side")
    photo(8, T, 48, 64, "PHOTO 01", "____ (48 × 64)", rx=1.2)
    y0 = T + 64
    t(8, y0 + 16, "JEONG", 30, "text", 200, ls=0.8)
    t(8, y0 + 27.5, "HYEOKJU", 30, "text", 200, ls=0.8)
    t(8, y0 + 34.5, "SPATIAL DESIGNER", 5.8, "text", 600, ls=0.3)
    t(8, y0 + 38.3, "공간 설계 디자이너 지원", 5.4, "sub", 400, fam=KR)
    para(8, y0 + 44, IDENT, S - 16, 5.2, fill="sub", fam=KR)
    menu = ["01  ABOUT", "02  WHAT I BRING", "03  EDUCATION · EXPERIENCE", "04  SKILLS", "05  COVER LETTER  →  P.2"]
    ym = y0 + 59
    for i, s_ in enumerate(menu):
        y = ym + i * 7
        ln(8, y, S - 8, y, "line", 0.2)
        t(8, y + 4.6, s_, 5.4, "text" if i == 0 else "sub", 600 if i == 0 else 500, ls=0.2)
    ln(8, ym + 35, S - 8, ym + 35, "line", 0.2)
    yn = ym + 49
    t(8, yn, "NUMBERS", 5.6, "text", 600, ls=0.3)
    for i, (lab, n, ko) in enumerate(NUMS):
        x, y = 8 + (i % 2) * 29, yn + 14 + (i // 2) * 19
        t(x, y, n, 20, "text", 200)
        t(x + 8.5, y - 4.4, lab, 4.6, "sub", 600, ls=0.2)
        t(x + 8.5, y - 0.6, ko, 4.8, "sub", 400, fam=KR)
    ln(8, yn + 48, S - 8, yn + 48, "line", 0.2)
    t(8, BOT - 25, "CONTACT", 5.6, "text", 600, ls=0.3)
    lines(8, BOT - 19.5, CONTACT + ["LANGUAGE  ____"], 5.4, 1.6, fill="sub", fam=KR)
    arrow(10, BOT, "GET IN TOUCH", 1.8)
    X = S + 10
    RW = 210 - X - 10

    def sec(y, label, right=""):
        ln(X, y, X + RW, y, "line", 0.25)
        t(X, y + 5, label, 5, "sub", 600, ls=0.35)
        if right:
            t(X + RW, y + 5, right, 4.8, "sub", 500, "end", ls=0.15)
    zone("T2C_03_ABOUT")
    sec(T, "ABOUT")
    t(X, T + 15, TITLE_KO[0], 15, "text", 400, fam=KR)
    t(X, T + 22.5, TITLE_KO[1], 15, "text", 400, fam=KR)
    t(X, T + 33, "PROFILE", 4.8, "text", 600, ls=0.25); lines(X, T + 37.2, PROFILE, 5.6, fill="sub", fam=KR)
    t(X + 60, T + 33, "INTERESTS", 4.8, "text", 600, ls=0.25); lines(X + 60, T + 37.2, INTERESTS, 5.6, fill="sub", fam=KR)
    zone("T2C_04_STRENGTHS")
    ys = T + 55
    sec(ys, "WHAT I BRING  ·  강점")
    for i, (n, en, ko, d) in enumerate(STRENGTHS):
        y = ys + 9 + i * 11.5
        t(X, y + 3.8, n, 6.4, "sub", 400)
        t(X + 9, y + 3.8, f"{en}  ·  {ko}", 6.6, "text", 600, fam=KR, ls=0.1)
        t(X + 9, y + 7.9, d, 5.6, "sub", 400, fam=KR)
        ln(X, y + 11, X + RW, y + 11, "line", 0.15)
    zone("T2C_05_EDUCATION_EXPERIENCE")
    yr = ys + 61
    sec(yr, "EDUCATION  ·  EXPERIENCE")
    for k, (title, body, per) in enumerate((("EDUCATION", EDU, "____ – ____"), ("EXPERIENCE", EXP, "____"))):
        y = yr + 9 + k * 19
        t(X, y + 3.2, per, 5.6, "sub", 500)
        t(X + 30, y + 3.2, title, 6.6, "text", 600, ls=0.2)
        for j, s_ in enumerate(body):
            para(X + 30, y + 7.6 + j * 3.6, s_, RW - 30, 5.6, fill="sub", fam=KR)
    zone("T2C_06_SKILLS")
    yk = yr + 50
    sec(yk, "SKILLS", "LANGUAGE  ____")
    t(X, yk + 9.5, FLOW, 4.6, "sub", 400, ls=0.1)
    cw = RW / 3
    for i, tool in enumerate(TOOLS):
        skill_v(X + (i % 3) * cw, yk + 13 + (i // 3) * 28, cw, tool, rr=5.5)
    zone("T2C_07_COVER_LETTER_LINK")
    yc = BOT - 20
    ln(X, yc, X + RW, yc, "line", 0.25)
    t(X, yc + 13, "COVER LETTER", 14, "text", 200, ls=0.3)
    t(X, BOT, "본인 소개와 강점 — 다음 장", 5.4, "sub", 400, fam=KR)
    arrow(X + RW - 22, yc + 13.5, "PAGE 2", 2.4, 5.4)
    zone("T2C_08_FOLIO")
    t(X, FOLIO + 1.5, "JEONG HYEOKJU  ·  CV", 5, "sub", 500, ls=0.3)
    t(X + RW, FOLIO + 1.5, "01 / 02", 5, "sub", 500, "end", ls=0.3)
    zone_end()


# ---- 2C · JAJU: same layout, content rebuilt from the JAJU rounding-VMD cover letter
#   (session 1_자기소개서_완료, docs/portfolio/jaju/jaju_rounding_vmd_q1_FINAL.md 2026-10-24, q2 / q3 FINAL 2026-10-25)
J_ROLE = ("ROUNDING VMD", "JAJU 라운딩 VMD 지원")
J_IDENT = "건축에서 배운 공간감과 패션에 대한 안목을 접목하려는 지원자"                        # Q1
J_TITLE = ("일상의 불편에서", "진열의 가능성을 찾다")                                           # Q1 subtitle
J_PROFILE = ["옷에 대한 관심은 건축보다 먼저", "건축으로 공간의 크기와 거리를 가늠하는 감각", "옷과 매장이 어떻게 보일지 기획하는 VMD를 목표로"]  # Q1
J_LOOK = ["어릴 때부터 매장에 들러 구경", "실내에 무엇이 어떻게 놓이는지", "스타일을 가리지 않고 입어 보기"]                    # Q1
J_STRENGTHS = [
    ("01", "OBSERVE", "일상의 불편", "일상의 작은 불편을 먼저 알아채고, 있는 것에서 바꿀 가능성을 찾습니다"),    # Q1
    ("02", "SPACE", "공간감", "상품 하나보다 매장 전체의 흐름 안에서 자리를 봅니다"),                            # Q1
    ("03", "STYLING", "패션에 대한 안목", "스타일을 가리지 않고 입어 보며 기른 안목 — 원단 · 디자인 · 색감"),      # Q1 + Q2
    ("04", "PREVIEW", "구상을 미리 확인", "진열을 바꾸기 전에 배치를 3D로 미리 그려 확인합니다"),                # Q2
]
J_RECORD = [
    ("____ – ____", "EDUCATION", ["____대학교 건축학과 (5년제)", "4학년 2학기 휴학 중"]),
    ("____", "EXPERIENCE", ["건축사사무소 ____ · 인턴 — 현장 실측 · 모델링 · 주변 대지와 프로젝트 건물 구현",
                            "실물 모형 제작 → 문화역서울284 기획전시 《돌봄의 디자인》 전시"]),                       # Q2
    ("2024.08 – 11", "PART-TIME", ["베이글 카페 — 창고 정리 제안 · 홀 테이블 재배치 · 매대 구분"]),               # Q3
]


def type2c_jaju():
    S, T = W_SIDE, TOP
    zone("T2J_01_BACKGROUND")
    r(0, 0, 210, 297, "bg")
    zone("T2J_02_SIDEBAR")
    r(0, 0, S, 297, "side")
    if TH.get("divider"):            # white version: sidebar keeps its width as a hairline, not a tint
        ln(S, 0, S, 297, "line", 0.25)
    photo(8, T, 48, 64, "PHOTO 01", "____ (48 × 64)", rx=1.2)
    y0 = T + 64
    t(8, y0 + 16, "JEONG", 30, "text", 200, ls=0.8)
    t(8, y0 + 27.5, "HYEOKJU", 30, "text", 200, ls=0.8)
    t(8, y0 + 34.5, J_ROLE[0], 5.8, "text", 600, ls=0.3)
    t(8, y0 + 38.3, J_ROLE[1], 5.4, "sub", 400, fam=KR)
    para(8, y0 + 44, J_IDENT, S - 16, 5.2, fill="sub", fam=KR)
    menu = ["01  ABOUT", "02  WHAT I BRING", "03  EDUCATION · EXPERIENCE", "04  SKILLS", "05  PORTFOLIO"]
    ym = y0 + 59
    for i, s_ in enumerate(menu):
        y = ym + i * 7
        ln(8, y, S - 8, y, "line", 0.2)
        t(8, y + 4.6, s_, 5.4, "text" if i == 0 else "sub", 600 if i == 0 else 500, ls=0.2)
    ln(8, ym + 35, S - 8, ym + 35, "line", 0.2)
    yn = ym + 49
    t(8, yn, "NUMBERS", 5.6, "text", 600, ls=0.3)
    for i, (lab, n, ko) in enumerate(NUMS):
        x, y = 8 + (i % 2) * 29, yn + 14 + (i // 2) * 19
        t(x, y, n, 20, "text", 200)
        t(x + 8.5, y - 4.4, lab, 4.6, "sub", 600, ls=0.2)
        t(x + 8.5, y - 0.6, ko, 4.8, "sub", 400, fam=KR)
    ln(8, yn + 48, S - 8, yn + 48, "line", 0.2)
    t(8, BOT - 25, "CONTACT", 5.6, "text", 600, ls=0.3)
    lines(8, BOT - 19.5, CONTACT + ["LANGUAGE  ____"], 5.4, 1.6, fill="sub", fam=KR)
    arrow(10, BOT, "GET IN TOUCH", 1.8)
    X = S + 10
    RW = 210 - X - 10

    def sec(y, label, right=""):
        ln(X, y, X + RW, y, "line", 0.25)
        t(X, y + 5, label, 5, "sub", 600, ls=0.35)
        if right:
            t(X + RW, y + 5, right, 4.8, "sub", 500, "end", ls=0.15)
    zone("T2J_03_ABOUT")
    sec(T, "ABOUT", "자기소개서 1번")
    t(X, T + 15, J_TITLE[0], 15, "text", 400, fam=KR)
    t(X, T + 22.5, J_TITLE[1], 15, "text", 400, fam=KR)
    t(X, T + 33, "PROFILE", 4.8, "text", 600, ls=0.25); lines(X, T + 37.2, J_PROFILE, 5.6, fill="sub", fam=KR)
    t(X + 64, T + 33, "LOOKING AT", 4.8, "text", 600, ls=0.25); lines(X + 64, T + 37.2, J_LOOK, 5.6, fill="sub", fam=KR)
    zone("T2J_04_STRENGTHS")
    ys = T + 55
    sec(ys, "WHAT I BRING  ·  강점", "자기소개서 1 · 2번")
    for i, (n, en, ko, d) in enumerate(J_STRENGTHS):
        y = ys + 9 + i * 11.5
        t(X, y + 3.8, n, 6.4, "sub", 400)
        t(X + 9, y + 3.8, f"{en}  ·  {ko}", 6.6, "text", 600, fam=KR, ls=0.1)
        t(X + 9, y + 7.9, d, 5.6, "sub", 400, fam=KR)
        ln(X, y + 11, X + RW, y + 11, "line", 0.15)
    zone("T2J_05_EDUCATION_EXPERIENCE")
    yr = ys + 61
    sec(yr, "EDUCATION  ·  EXPERIENCE")
    y = yr + 9
    for per, title, body in J_RECORD:
        t(X, y + 3.2, per, 5.6, "sub", 500)
        t(X + 30, y + 3.2, title, 6.6, "text", 600, ls=0.2)
        yy = y + 7.6
        for s_ in body:
            yy = para(X + 30, yy, s_, RW - 30, 5.6, fill="sub", fam=KR) + 0.6
        y = max(yy, y + 12) + 3.4
    zone("T2J_06_SKILLS")
    yk = y + 2
    sec(yk, "SKILLS", "LANGUAGE  ____")
    t(X, yk + 9.5, FLOW, 4.6, "sub", 400, ls=0.1)
    cw = RW / 3
    for i, tool in enumerate(TOOLS):
        skill_v(X + (i % 3) * cw, yk + 12.5 + (i // 3) * 24.5, cw, tool, rr=5.2)
    zone("T2J_07_PORTFOLIO_LINK")
    yc = BOT - 12
    ln(X, yc, X + RW, yc, "line", 0.25)
    t(X, BOT, "PORTFOLIO", 10, "text", 200, ls=0.3)
    t(X + 30, BOT, "패션에 대한 안목은 포트폴리오에 — 별도 첨부", 5.4, "sub", 400, fam=KR)
    arrow(X + RW - 14, BOT - 1, "VIEW", 2.0, 5)
    zone("T2J_08_FOLIO")
    t(X, FOLIO + 1.5, "JEONG HYEOKJU  ·  CV", 5, "sub", 500, ls=0.3)
    t(X + RW, FOLIO + 1.5, "JAJU  ·  ROUNDING VMD", 5, "sub", 500, "end", ls=0.3)
    zone_end()
    return yk + 12.5 + 24.5 + 21      # bottom of the skill badges, for the fit check


WHITE = dict(bg="#FFFFFF", card="#F2F2F0", side="#FFFFFF", photo="#ECECEA", px="#D2D2CF",
             text="#141414", sub="#6B6A67", line="#D6D6D3", grid="#E6E6E3", divider=True)
# the grey adopted for the Gentle Monster CV page 2 (page2.GRAY): page #2E2E2E, sidebar one step lighter
GRAY = dict(bg="#2E2E2E", card="#3A3A3A", side="#3A3A3A", photo="#444444", px="#555555",
            text="#ECE8E1", sub="#A9A59F", line="#4A4A4A", grid="#3A3A3A")


def export(fn, stem, title, th=None, out_dir=None, ai=True):
    bp.OUT.clear()
    w('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">')
    w(f'<title>{title}</title>')
    w('<defs><pattern id="hatch" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
      '<rect width="1.2" height="1.2" fill="#262626"/><line x1="0" y1="0" x2="0" y2="1.2" stroke="#8E8B86" stroke-width="0.4"/></pattern></defs>')
    theme(th or DARK)
    fn()
    w('</svg>')
    svg = Path(out_dir or AI) / f"{stem}.svg"
    svg.write_text("\n".join(bp.OUT), encoding="utf-8")
    if not ai:
        return svg
    pdf = svg.with_suffix(".pdf")
    subprocess.run(["inkscape", str(svg), "--export-type=pdf", "--export-pdf-version=1.5", f"--export-filename={pdf}"],
                   check=True, capture_output=True)
    pdf.replace(svg.with_suffix(".ai"))
    print(svg.with_suffix(".ai"))
    return svg


def main():
    export(type2b, "CV_TYPE2B_SIDEBAR", "CV 1/2 · TYPE 2B SIDEBAR (photo 48 x 64) · JEONG HYEOKJU")
    export(type2c, "CV_TYPE2C_SIDEBAR", "CV 1/2 · TYPE 2C SIDEBAR (1/3, portfolio proportions) · JEONG HYEOKJU")
    export(type2c_jaju, "CV_TYPE2C_JAJU", "CV · TYPE 2C · JAJU ROUNDING VMD · JEONG HYEOKJU")
    # InDesign only (user, 2026-10-25): white, and the grey of the Gentle Monster CV page 2
    import svg2idml
    ind = AI.parent / "indesign"
    # IVORY = the light beige of the Gentle Monster CV page 2, first B option (bp.LIGHT, #E6E2DA) — user, 2026-10-25
    for tag, th in (("WHITE", WHITE), ("GRAY", GRAY), ("IVORY", LIGHT)):
        svg = export(type2c_jaju, f"CV_TYPE2C_JAJU_{tag}", f"CV · TYPE 2C · JAJU ROUNDING VMD · {tag} · JEONG HYEOKJU",
                     th=th, out_dir=ind, ai=False)
        svg2idml.main(str(svg), str(ind / f"CV_TYPE2C_JAJU_{tag}.idml"))


def _old_main():
    bp.OUT.clear()
    w('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">')
    w('<title>CV 1/2 · TYPE 2B SIDEBAR (photo 48 x 64) · JEONG HYEOKJU</title>')
    w('<defs><pattern id="hatch" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
      '<rect width="1.2" height="1.2" fill="#262626"/><line x1="0" y1="0" x2="0" y2="1.2" stroke="#8E8B86" stroke-width="0.4"/></pattern></defs>')
    theme(DARK)
    type2b()
    w('</svg>')
    svg = AI / "CV_TYPE2B_SIDEBAR.svg"
    svg.write_text("\n".join(bp.OUT), encoding="utf-8")
    pdf = svg.with_suffix(".pdf")
    subprocess.run(["inkscape", str(svg), "--export-type=pdf", "--export-pdf-version=1.5", f"--export-filename={pdf}"],
                   check=True, capture_output=True)
    pdf.replace(svg.with_suffix(".ai"))
    print(svg.with_suffix(".ai"))


if __name__ == "__main__":
    main()
