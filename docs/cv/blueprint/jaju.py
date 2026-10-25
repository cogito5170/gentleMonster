"""CV 1/2 (TYPE 1, card grid) re-toned for JAJU — three tone options, same layout and copy.

    python3 docs/cv/blueprint/jaju.py   # -> types/E-00.svg, jaju_v3_options.pdf, ../ai/CV_JAJU_TYPE1_J*.ai

Colour source: press coverage of the JAJU rebranding (Dec 2024) — it dropped the achromatic image and took
colour and pattern from Korean nature and tradition: patterns of bean pods, charcoal and dried chilli,
packaging with hemp, ceramic and wood textures. The hex values below are picked from those materials;
they are NOT JAJU's official brand colours.
"""
import subprocess
from pathlib import Path

from bp import *  # noqa: F401,F403
import bp
from cv_types import (CONTACT, EDU, EXP, FLOW, IDENT, INTERESTS, PROFILE, STRENGTHS, TITLE_KO, TOOLS,
                      nav_pills, type1)

HERE = Path(__file__).parent
AI = HERE.parent / "ai"

TONES = [
    dict(code="J1", en="HEMP", ko="삼베", note="바탕 삼베 · 글자 숯 · 강조 말린 고추",
         th=dict(bg="#E7DFD0", card="#DCD2C0", side="#DCD2C0", photo="#CBBFA9", px="#B7AA92",
                 text="#24221F", sub="#625C52", line="#C2B7A2", grid="#D2C8B5", accent="#9C3A26", on_accent="#F4EEE4")),
    dict(code="J2", en="PORCELAIN", ko="백자", note="바탕 백자 · 글자 숯 · 강조 콩깍지",
         th=dict(bg="#F1EEE7", card="#E5E0D5", side="#E5E0D5", photo="#D3CDC0", px="#BDB6A7",
                 text="#1F1E1C", sub="#5F5B54", line="#CFC9BD", grid="#DDD7CB", accent="#6F7148", on_accent="#F4F1EA")),
    dict(code="J3", en="CHARCOAL", ko="숯", note="바탕 숯 · 글자 한지 · 강조 말린 고추",
         th=dict(bg="#1F1D1B", card="#2B2825", side="#2B2825", photo="#393531", px="#4A4540",
                 text="#EDE6DA", sub="#A39C91", line="#3C3833", grid="#2B2825", accent="#B4482F", on_accent="#F6EFE6")),
]


def jaju_v2():
    """TYPE 1 without the FRAME & INTERIOR hero: a profile block takes the top, the rest is redistributed."""
    M, CW, G = 7, 196, 2.5
    hw = (CW - G) / 2
    zone("J_01_BACKGROUND")
    r(0, 0, 210, 297, "bg")
    zone("J_02_NAV")
    t(M + 1, 12.6, "JEONG HYEOKJU", 7, "text", 600, ls=0.35)
    nav_pills()
    zone("J_03_PROFILE")
    pw = 52.5
    lw = CW - G - pw
    r(M, 18, lw, 62, "card", rx=1.6)
    t(M + 6, 25.5, "PROFILE", 5, "text", 600, ls=0.3)
    t(M + 6, 39, "정혁주", 22, "text", 400, fam=KR, ls=0.6)
    t(M + 6, 46.5, "JEONG HYEOKJU", 10, "text", 300, ls=1.2)
    t(M + 6, 53.5, "APPLYING FOR  ·  ____ (자주 지원 직무)", 6, "text", 600, ls=0.2)
    t(M + 6, 57.6, IDENT, 5.6, "sub", 400, fam=KR)
    ln(M + 6, 63.5, M + lw - 6, 63.5, "line", 0.25)
    info = [("MAJOR", "건축학 · 5년제"), ("STATUS", "4학년 2학기 휴학"), ("INTERNSHIP", "건축사사무소 ____"), ("TOOLS", "2D · 3D · 렌더 · 후보정")]
    cw4 = (lw - 12) / 4
    for i, (k, v) in enumerate(info):
        t(M + 6 + i * cw4, 68.5, k, 4.6, "sub", 600, ls=0.3)
        t(M + 6 + i * cw4, 73.5, v, 5.6, "text", 400, fam=KR)
    photo(M + lw + G, 18, pw, 62, "PHOTO 01", "인물 사진 ____", rx=1.6)
    zone("J_04_STRENGTH_CARDS")
    cw = (CW - 3 * G) / 4
    for i, (n, en, ko, d) in enumerate(STRENGTHS):
        x = M + i * (cw + G)
        r(x, 83, cw, 28, "card", rx=1.6)
        t(x + 3.5, 88.5, f"{n}  {en}", 5.6, "text", 600, ls=0.2)
        t(x + 3.5, 92.3, ko, 5.2, "sub", 500, fam=KR)
        para(x + 3.5, 97, d, cw - 7, 5.0, fill="sub", fam=KR)
        arrow(x + 5.4, 106.4, "P.2", 1.7)
    zone("J_05_NUMBERS")
    stats = [("5-YEAR B.ARCH", "5", "5년제 건축학과"), ("DESIGN STUDIOS", "7", "설계 수업 7학기"),
             ("TOOLS", "6", "2D · 3D · 후보정"), ("INTERNSHIP", "1", "건축사사무소")]
    for i, (lab, n, ko) in enumerate(stats):
        x = M + 1 + i * 49.5
        t(x, 117, lab, 4.8, "sub", 500, ls=0.25)
        t(x, 125.5, n, 17, "text", 200)
        t(x + 7.5, 125.5, ko, 5, "sub", 400, fam=KR)
    zone("J_06_ABOUT")
    r(M, 131, hw, 48, "card", rx=1.6)
    t(M + 5, 137.5, "ABOUT", 5, "text", 600, ls=0.3)
    t(M + 5, 147, TITLE_KO[0], 12, "text", 400, fam=KR)
    t(M + 5, 152.8, TITLE_KO[1], 12, "text", 400, fam=KR)
    t(M + 5, 161.5, "PROFILE", 4.8, "text", 600, ls=0.25); lines(M + 5, 165.3, PROFILE, 5.2, fill="sub", fam=KR)
    t(M + 50, 161.5, "INTERESTS", 4.8, "text", 600, ls=0.25); lines(M + 50, 165.3, INTERESTS, 5.2, fill="sub", fam=KR)
    photo(M + hw + G, 131, hw, 48, "PHOTO 02", "____ (공간 · 마감재 · 오브제)", rx=1.6)
    zone("J_07_EDUCATION_EXPERIENCE")
    eh = (98 - G) / 2
    for k, (title, body, slot) in enumerate((("EDUCATION", EDU, "____ – ____"), ("EXPERIENCE", EXP, "____"))):
        y = 182 + k * (eh + G)
        r(M, y, hw, eh, "card", rx=1.6)
        t(M + 5, y + 7, title, 7, "text", 600, ls=0.3)
        for j, s in enumerate(body):
            para(M + 5, y + 13 + j * 4.2, s, hw - 10, 5.8, fill="sub", fam=KR)
        arrow(M + hw - 26, y + eh - 7, slot)
    zone("J_08_SKILLS")
    x2 = M + hw + G
    r(x2, 182, hw, 98, "card", rx=1.6)
    t(x2 + 5, 189, "SKILLS", 7, "text", 600, ls=0.3)
    t(x2 + hw - 5, 189, "LANGUAGE  ____", 4.8, "sub", 500, "end", ls=0.15)
    t(x2 + 5, 193.5, FLOW, 4.4, "sub", 400, ls=0.1)
    for i, tool in enumerate(TOOLS):
        skill_h(x2 + 5 + (i % 2) * 45, 199 + (i // 2) * 27, tool, rr=6, name_pt=6, small=5)
    zone("J_09_FOOTER_CONTACT")
    yF = 282.5
    r(M, yF, CW, 290 - yF, "card", rx=1.6)
    t(M + 4, yF + 4.7, "CONTACT", 5.6, "text", 600, ls=0.25)
    for i, s in enumerate(CONTACT):
        t(M + 30 + i * 36, yF + 4.7, s, 5.2, "sub", 400, fam=KR)
    arrow(M + CW - 28, yF + 3.75, "GET IN TOUCH", 1.7)
    zone_end()


# ---- v3: smaller top block, three larger strength cards (JAJU cover letter, session 1_자기소개서, Q1-Q3 final)
JAJU_ROLE = "ROUNDING VMD  ·  라운딩 VMD  ·  JAJU"
JAJU_IDENT = "건축에서 배운 공간감과 패션에 대한 안목을 접목하려는 지원자"          # Q1, first sentence
CARDS_A = [  # Q1 'two things' + Q2 'two abilities' -> space, styling, preview
    ("01", "SPACE", "공간감", "상품 하나보다 매장 전체의 흐름 안에서 자리를 봅니다.",
     "건축 · 공간의 크기와 거리를 가늠하는 감각", "자기소개서 1번"),
    ("02", "STYLING", "스타일링 감각", "원단과 디자인, 색감이 한데 어우러지는지부터 봅니다.",
     "지인 스타일링 — 분위기를 먼저 찾고 안경 · 상의 · 하의를 고름", "자기소개서 2번"),
    ("03", "PREVIEW", "구상을 미리 확인하는 능력", "진열을 바꾸기 전에 배치를 3D로 미리 그려 확인합니다.",
     "인턴 실물 모형 → 문화역서울284 《돌봄의 디자인》 전시", "자기소개서 2번"),
]
CARDS_B = [  # observation (Q1 + Q3) instead of space
    ("01", "OBSERVE", "일상의 불편", "일상의 작은 불편을 먼저 알아채고, 해결할 수 있는 가능성을 찾습니다.",
     "카페 창고 · 홀 · 매대를 있던 물건으로 다시 정리 (2024.8–11)", "자기소개서 1 · 3번"),
    CARDS_A[1], CARDS_A[2],
]


def jaju_v3(cards=CARDS_A):
    M, CW, G = 7, 196, 2.5
    hw = (CW - G) / 2
    zone("J_01_BACKGROUND")
    r(0, 0, 210, 297, "bg")
    zone("J_02_NAV")
    t(M + 1, 12.6, "JEONG HYEOKJU", 7, "text", 600, ls=0.35)
    nav_pills()
    zone("J_03_PROFILE")
    ph_w = 30                                     # ID-photo ratio 3:4 at 38 high (30 x 38 ~ 0.79)
    lw = CW - G - ph_w
    r(M, 18, lw, 38, "card", rx=1.6)
    t(M + 6, 31, "정혁주", 18, "text", 400, fam=KR, ls=0.5)
    t(M + 37, 31, "JEONG HYEOKJU", 9, "text", 300, ls=1.0)
    t(M + 6, 39.5, JAJU_ROLE, 6.2, "text", 600, ls=0.2)
    t(M + 6, 44, JAJU_IDENT, 5.6, "sub", 400, fam=KR)
    info = [("MAJOR", "건축학 · 5년제"), ("STATUS", "4학년 2학기 휴학"), ("INTERNSHIP", "건축사사무소 ____"), ("TOOLS", "2D · 3D · 렌더 · 후보정")]
    ix = M + 6 + (lw - 12) * 0.58
    for i, (k, v) in enumerate(info):
        x, y = ix + (i % 2) * 33, 25 + (i // 2) * 11
        t(x, y, k, 4.6, "sub", 600, ls=0.3)
        t(x, y + 4.6, v, 5.6, "text", 400, fam=KR)
    ln(ix - 4, 22, ix - 4, 52, "line", 0.25)
    photo(M + lw + G, 18, ph_w, 38, "PHOTO 01", "____", rx=1.6)
    zone("J_04_STRENGTH_CARDS")
    cw = (CW - 2 * G) / 3
    for i, (n, en, ko, line, proof, src) in enumerate(cards):
        x = M + i * (cw + G)
        r(x, 59, cw, 42, "card", rx=1.6)
        t(x + 5, 66, f"{n}  {en}", 7, "text", 600, ls=0.3)
        t(x + 5, 72.5, ko, 8.4, "text", 700, fam=KR)
        para(x + 5, 79.5, line, cw - 10, 6.2, 1.45, fill="text", fam=KR)
        ln(x + 5, 90.5, x + cw - 5, 90.5, "line", 0.2)
        para(x + 5, 94.3, proof, cw - 10, 5.0, 1.4, fill="sub", fam=KR)
        t(x + cw - 5, 66, src, 4.6, "sub", 500, "end", fam=KR)
    zone("J_05_NUMBERS")
    stats = [("5-YEAR B.ARCH", "5", "5년제 건축학과"), ("DESIGN STUDIOS", "7", "설계 수업 7학기"),
             ("TOOLS", "6", "2D · 3D · 후보정"), ("INTERNSHIP", "1", "건축사사무소")]
    for i, (lab, n, ko) in enumerate(stats):
        x = M + 1 + i * 49.5
        t(x, 108, lab, 4.8, "sub", 500, ls=0.25)
        t(x, 116.5, n, 17, "text", 200)
        t(x + 7.5, 116.5, ko, 5, "sub", 400, fam=KR)
    zone("J_06_ABOUT")
    r(M, 121, hw, 48, "card", rx=1.6)
    t(M + 5, 127.5, "ABOUT", 5, "text", 600, ls=0.3)
    t(M + 5, 137, TITLE_KO[0], 12, "text", 400, fam=KR)
    t(M + 5, 142.8, TITLE_KO[1], 12, "text", 400, fam=KR)
    t(M + 5, 151.5, "PROFILE", 4.8, "text", 600, ls=0.25); lines(M + 5, 155.3, PROFILE, 5.2, fill="sub", fam=KR)
    t(M + 50, 151.5, "INTERESTS", 4.8, "text", 600, ls=0.25); lines(M + 50, 155.3, INTERESTS, 5.2, fill="sub", fam=KR)
    photo(M + hw + G, 121, hw, 48, "PHOTO 02", "____ (공간 · 마감재 · 오브제)", rx=1.6)
    zone("J_07_EDUCATION_EXPERIENCE")
    gh = 108
    eh = (gh - G) / 2
    for k, (title, body, slot) in enumerate((("EDUCATION", EDU, "____ – ____"), ("EXPERIENCE", EXP, "____"))):
        y = 172 + k * (eh + G)
        r(M, y, hw, eh, "card", rx=1.6)
        t(M + 5, y + 7, title, 7, "text", 600, ls=0.3)
        for j, s_ in enumerate(body):
            para(M + 5, y + 13 + j * 4.2, s_, hw - 10, 5.8, fill="sub", fam=KR)
        arrow(M + hw - 26, y + eh - 7, slot)
    zone("J_08_SKILLS")
    x2 = M + hw + G
    r(x2, 172, hw, gh, "card", rx=1.6)
    t(x2 + 5, 179, "SKILLS", 7, "text", 600, ls=0.3)
    t(x2 + hw - 5, 179, "LANGUAGE  ____", 4.8, "sub", 500, "end", ls=0.15)
    t(x2 + 5, 183.5, FLOW, 4.4, "sub", 400, ls=0.1)
    for i, tool in enumerate(TOOLS):
        skill_h(x2 + 5 + (i % 2) * 45, 190 + (i // 2) * 30, tool, rr=6, name_pt=6, small=5)
    zone("J_09_FOOTER_CONTACT")
    yF = 282.5
    r(M, yF, CW, 290 - yF, "card", rx=1.6)
    t(M + 4, yF + 4.7, "CONTACT", 5.6, "text", 600, ls=0.25)
    for i, s_ in enumerate(CONTACT):
        t(M + 30 + i * 36, yF + 4.7, s_, 5.2, "sub", 400, fam=KR)
    arrow(M + CW - 28, yF + 3.75, "GET IN TOUCH", 1.7)
    zone_end()


def jaju_v3b():
    jaju_v3(CARDS_B)


LAYOUT = jaju_v3   # v3: smaller top, three cards (user, 2026-10-25)


def review(path, tone):
    """E-02: before (v2) | v3 card set A | v3 card set B, one tone."""
    sheet_open()
    t(16, 17, "E-02   JAJU 1페이지 · 위 블록 줄이고 강점 카드 3개로  ·  검토", 10, INK, 700, ls=0.3, fam=KR)
    t(16, 22.5, f"같은 색({tone['code']} {tone['ko']})에서 비교. 카드의 글은 '1_자기소개서' 세션의 자주 라운딩 VMD 자기소개서 1~3번 확정본에서 그대로 가져옴.",
      6.0, INK2, 400, fam=KR)
    s, gx, gy, gap = 0.6, 16, 30, 7
    pw, ph = 210 * s, 297 * s
    cols = [("현재 (v2)", jaju_v2, "프로필 62 · 강점 카드 4개 × 28"),
            ("검토안 A", jaju_v3, "프로필 38 · 카드 3개 × 42: 공간감 · 스타일링 · 미리 확인"),
            ("검토안 B", jaju_v3b, "프로필 38 · 카드 3개 × 42: 일상의 불편 · 스타일링 · 미리 확인")]
    for i, (name, fn, note) in enumerate(cols):
        x = gx + i * (pw + gap)
        drawing(fn, x, gy, s, tone["th"])
        zone_end()
        r(x, gy, pw, ph, stroke=INK, sw=0.25)
        t(x, gy + ph + 5.5, name, 8, INK, 700, fam=KR)
        para(x, gy + ph + 9.6, note, pw, 5.4, 1.4, fill=INK2, fam=KR)
    yb = 232
    ln(16, yb - 4, 404, yb - 4, RULE, 0.3)
    notes = ["· 위 블록 62 → 38: 이름(국문 18pt · 영문)과 직무 · 한 줄 소개는 왼쪽, 전공 · 상태 · 인턴 · 툴은 오른쪽 2 × 2 로 옮겨 한 줄을 없앰. 인물 사진은 증명사진 비율(30 × 38).",
             "· 직무 줄: ROUNDING VMD · 라운딩 VMD · JAJU. 한 줄 소개는 자기소개서 1번 첫 문장 '건축에서 배운 공간감과 패션에 대한 안목을 접목하려는 지원자'.",
             "· 강점 카드 4 × 28 → 3 × 42: 영문 제목 7pt · 국문 8.4pt · 한 줄 6.2pt (전 5pt) · 근거 한 줄. 젠틀몬스터용 'P.2' 화살표는 빼고 근거 문항 번호를 적음.",
             "· A 는 자기소개서 1번 '두 가지'(공간감 · 패션 안목)와 2번 '두 능력'(스타일링 · 미리 확인)을 합친 셋. B 는 공간감 대신 1 · 3번의 '일상의 불편'(카페 창고 · 홀 정리).",
             "· 그대로 둔 곳: ABOUT 카드는 아직 젠틀몬스터 자기소개서 제목 '틀을 배우고, 그 안을 채우는 건축학도'와 '공간 디자인으로 전향' — 자주용으로 바꿀지 따로 정해야 함."]
    y = yb
    for s_ in notes:
        y = para(16, y, s_, 388, 5.8, 1.5, fill=INK, fam=KR) + 1.2
    sheet_close(path)


def a4(tone, path):
    bp.OUT.clear()
    w('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">')
    w(f'<title>CV 1/2 · JAJU · {tone["code"]} {tone["en"]} · JEONG HYEOKJU</title>')
    theme(tone["th"])
    LAYOUT()
    zone_end()
    w('</svg>')
    path.write_text("\n".join(bp.OUT), encoding="utf-8")


def overview(path):
    sheet_open()
    t(16, 17, "E-01   CV 1/2 · FOR JAJU  ·  NO HERO  ·  3 TONES", 10, INK, 700, ls=0.3)
    t(16, 22.5, "TYPE 1 에서 첫 화면(FRAME & INTERIOR)을 빼고 다시 짠 자주(JAJU)용 1페이지. 위에 프로필 블록, 아래로 강점 · 숫자 · ABOUT · 학력 · 경력 · 스킬. "
                "색은 자주 리브랜딩 보도에 나온 재료(삼베 · 백자 · 숯 · 말린 고추 · 콩깍지)에서 고름 — 공식 브랜드 색 아님.",
      6.0, INK2, 400, fam=KR)
    s, gx, gy, gap = 0.6, 16, 30, 7
    pw, ph = 210 * s, 297 * s
    for i, tone in enumerate(TONES):
        x = gx + i * (pw + gap)
        drawing(LAYOUT, x, gy, s, tone["th"])
        bp.zone_end()
        r(x, gy, pw, ph, stroke=INK, sw=0.25)
        cy = gy + ph + 5.5
        t(x, cy, f"{tone['code']}  {tone['en']}", 8, INK, 700, ls=0.3)
        t(x + pw, cy, tone["ko"], 6, INK2, 500, "end", fam=KR)
        t(x, cy + 4.4, tone["note"], 5.4, INK, 400, fam=KR)
        keys = [("bg", "바탕"), ("card", "카드"), ("text", "글자"), ("sub", "본문"), ("accent", "강조")]
        for k, (key, lab) in enumerate(keys):
            sx = x + k * 25
            r(sx, cy + 7, 23, 5, tone["th"][key], INK, 0.15)
            t(sx, cy + 15, lab, 4.8, INK, 500, fam=KR)
            t(sx, cy + 17.6, tone["th"][key], 4.4, INK2, 400)
    yb = 262
    ln(16, yb - 4, 404, yb - 4, RULE, 0.3)
    notes = ["· 뺀 것: 첫 화면(사진 + FRAME & INTERIOR, 높이 95). 이름 · 직무 · 한 줄 소개는 위 프로필 블록(높이 62)으로 옮김, 인물 사진은 그 오른쪽 세로 칸.",
             "· 다시 나눈 것: 프로필 62 · 강점 카드 28 · 숫자 줄 14(rev.B 에서 되살림) · ABOUT 48 · 학력/경력 + 스킬 98 · 연락처 7.5. 글은 그대로.",
             "· 직무 자리는 ____ (자주 지원 직무) 로 비워 둠 — 젠틀몬스터 직무명(공간 설계 디자이너)을 자주 서류에 남기지 않으려고.",
             "· 근거: 자주는 2024년 12월 리브랜딩에서 무채색을 버리고 한국의 자연 · 전통에서 색과 문양을 가져옴 (한경 매거진 · 머니투데이 보도)."]
    lines(16, yb, notes, 5.8, 1.55, fill=INK, fam=KR)
    sheet_close(path)


def main():
    out = HERE / "types"
    pdfs = []
    ov = out / "E-02.svg"
    review(ov, TONES[1])
    svgs = [ov]
    for tone in TONES:
        p = out / f"jaju_v3_{tone['code']}.svg"
        a4(tone, p)
        svgs.append(p)
    for svg in svgs:
        pdf = svg.with_suffix(".pdf")
        subprocess.run(["inkscape", str(svg), "--export-type=pdf", f"--export-filename={pdf}"], check=True, capture_output=True)
        pdfs.append(str(pdf))
    subprocess.run(["pdfunite", *pdfs, str(HERE / "jaju_v3_options.pdf")], check=True)
    for tone in TONES:          # Illustrator copies
        stem = f"CV_JAJU_V3_{tone['code']}_{tone['en']}"
        svg = AI / f"{stem}.svg"
        a4(tone, svg)
        pdf = AI / f"{stem}.pdf"
        subprocess.run(["inkscape", str(svg), "--export-type=pdf", "--export-pdf-version=1.5", f"--export-filename={pdf}"],
                       check=True, capture_output=True)
        pdf.replace(AI / f"{stem}.ai")
        print(AI / f"{stem}.ai")
    print(HERE / "jaju_v3_options.pdf")


if __name__ == "__main__":
    main()
