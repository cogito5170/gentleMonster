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


def main():
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
