"""JAJU rounding-VMD CV, built on the applicant's own InDesign form '클로드.idml' (TYPE 2C, white, 1/3 sidebar).

    python3 docs/cv/blueprint/cv_jaju_v4.py <클로드.idml> docs/cv/indesign/CV_JAJU_V4.idml

- The form keeps its own package (master, styles, layer, the placed photo frame with its link IMG_5685.psd, the
  name '정혁주' in Pretendard Light). Only the page items are replaced by this re-layout, and the photo frame is
  carried over untouched.
- Content: facts from the Gentle Monster CV the applicant finished (education timeline, a.co.lab internship,
  NY bagel cafe, contact) + the JAJU cover letter finals (Q1-Q3). GM-only lines are dropped or re-aimed at JAJU.
- Type sizes follow that GM CV (measured on the image: section heads ~10 pt, sub-title 13 pt, body 7.5 pt,
  card titles 9 pt, small labels 6-7 pt, skill ring 13 mm).
"""
import re
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bp  # noqa: E402
from bp import *  # noqa: F401,F403,E402
import idml_writer as IW  # noqa: E402
import svg2idml  # noqa: E402
from cv_types import TOOLS  # noqa: E402
from type2b import BOT, FOLIO, J_IDENT, J_PROFILE, J_STRENGTHS, J_TITLE, TOP, W_SIDE, WHITE  # noqa: E402

PRET = "Pretendard, 'Noto Sans CJK KR', sans-serif"

# ---- facts (GM CV image, user-confirmed edits 2026-10-25: JAJU line, Hyeokju, EDITORIAL)
EDUCATION = [("2020 – 2022", "서울시립대학교 건축학과 입학"),
             ("2022 – 2024", "육군 병장 만기 전역  *표창 수상 2회"),
             ("2024", "서울시립대학교 건축학과 복학 및 휴학"),
             ("2024 – 2025", "건축 공부 & 헤비타트 봉사, 아르바이트"),
             ("2025 – 2026", "서울시립대학교 건축학과 복학 및 휴학"),
             ("Now. 2026", "JAJU 라운딩 VMD 지원")]
EXPERIENCE = [("", "건축사사무소 (a.co.lab)  ·  인턴",
               ["현장 실측 · 모델링 · 주변 대지와 프로젝트 건물 구현",
                "실물 모형 제작 → 문화역서울284 기획전시 《돌봄의 디자인》 전시"]),
              ("2024.08 – 11", "카페 (뉴욕라츠오베이글스)  ·  아르바이트",
               ["창고 수납 정리 구축 · 업무 체계화 · 테이블 및 식물 재배치로 공간 개선"])]
INTERESTS = ["패션 · 공간", "가구와 조명 수집", "건축물의 실내 마감재와 마감 방식"]
CONTACT = ["T. 010-8582-3257", "E. aa3391@naver.com", "PORTFOLIO _Jeong Hyeokju"]
NUMS = (("B.ARCH", "5", "5년제"), ("STUDIOS", "7", "설계 7학기"), ("TOOLS", "6", "2D–편집"), ("INTERN", "1", "건축사사무소"))
FLOW = "2D → 3D → RENDER → RETOUCH → GRAPHIC → EDITORIAL"
PHOTO = (8, TOP, 48, 64)            # the form's photo frame — kept where it is


def layout():
    S, T = W_SIDE, TOP
    zone("J4_01_BACKGROUND")
    r(0, 0, 210, 297, "bg")
    zone("J4_02_SIDEBAR")
    r(0, 0, S, 297, "side")
    ln(S, 0, S, 297, "line", 0.25)
    # photo: the form's own frame is inserted here by build(), nothing is drawn
    y0 = T + PHOTO[3]
    t(8, y0 + 18, "정혁주", 30, "text", 300, fam=PRET, ls=0.6)
    t(8, y0 + 26.5, "ROUNDING VMD", 7.5, "text", 600, ls=0.35)
    t(8, y0 + 30.7, "JAJU 라운딩 VMD 지원", 7.5, "sub", 400, fam=KR)
    para(8, y0 + 36.6, J_IDENT, S - 16, 7.5, 1.45, fill="sub", fam=KR)
    menu = ["01  ABOUT", "02  WHAT I BRING", "03  EDUCATION · EXPERIENCE", "04  SKILLS", "05  PORTFOLIO"]
    ym = y0 + 49
    for i, s_ in enumerate(menu):
        y = ym + i * 7.2
        ln(8, y, S - 8, y, "line", 0.2)
        t(8, y + 4.8, s_, 7, "text" if i == 0 else "sub", 600 if i == 0 else 500, ls=0.2)
    ln(8, ym + 36, S - 8, ym + 36, "line", 0.2)
    yn = ym + 49
    t(8, yn, "NUMBERS", 9, "text", 600, ls=0.35)
    for i, (lab, n, ko) in enumerate(NUMS):
        x, y = 8 + (i % 2) * 29, yn + 15 + (i // 2) * 19
        t(x, y, n, 22, "text", 200)
        t(x + 9, y - 4.6, lab, 6.2, "sub", 600, ls=0.2)
        t(x + 9, y - 0.4, ko, 7, "sub", 400, fam=KR)
    ln(8, yn + 48, S - 8, yn + 48, "line", 0.2)
    t(8, BOT - 27, "CONTACT", 9, "text", 600, ls=0.35)
    lines(8, BOT - 20.5, CONTACT, 7.5, 1.6, fill="sub", fam=KR)
    arrow(10, BOT, "GET IN TOUCH", 1.9, 6.5)
    X = S + 10
    RW = 210 - X - 10

    def sec(y, label, right=""):
        ln(X, y, X + RW, y, "line", 0.3)
        t(X, y + 5.6, label, 10, "text", 600, ls=0.45)
        if right:
            t(X + RW, y + 5.2, right, 6.2, "sub", 500, "end", fam=KR)
    zone("J4_03_ABOUT")
    sec(T, "ABOUT", "자기소개서 1번")
    t(X, T + 16, J_TITLE[0], 13, "text", 400, fam=KR)
    t(X, T + 22.6, J_TITLE[1], 13, "text", 400, fam=KR)
    t(X, T + 31.4, "PROFILE", 8, "text", 600, ls=0.35)
    lines(X, T + 36, J_PROFILE, 7.5, 1.45, fill="sub", fam=KR)
    t(X + 66, T + 31.4, "INTERESTS", 8, "text", 600, ls=0.35)
    lines(X + 66, T + 36, INTERESTS, 7.5, 1.45, fill="sub", fam=KR)
    zone("J4_04_STRENGTHS")
    ys = T + 49
    sec(ys, "WHAT I BRING", "자기소개서 1 · 2번")
    for i, (n, en, ko, d) in enumerate(J_STRENGTHS):
        y = ys + 9 + i * 11.3
        t(X, y + 4.2, n, 7.5, "sub", 400)
        t(X + 9, y + 4.2, f"{en}  ·  {ko}", 9, "text", 600, fam=KR, ls=0.1)
        t(X + 9, y + 8.6, d, 7.5, "sub", 400, fam=KR)
        ln(X, y + 11, X + RW, y + 11, "line", 0.15)
    zone("J4_05_EDUCATION_EXPERIENCE")
    yr = ys + 58.5
    sec(yr, "EDUCATION · EXPERIENCE")
    t(X, yr + 12, "EDUCATION", 8, "text", 600, ls=0.35)
    y = yr + 16.6
    for per, s_ in EDUCATION:
        t(X, y, per, 7.2, "sub", 500)
        t(X + 26, y, s_, 7.5, "text", 400, fam=KR)
        y += 4.2
    t(X, y + 2.6, "EXPERIENCE", 8, "text", 600, ls=0.35)
    y += 7.2
    for per, head, body in EXPERIENCE:
        t(X, y, per, 7.2, "sub", 500)
        t(X + 26, y, head, 7.5, "text", 600, fam=KR)
        y += 4.2
        for s_ in body:
            y = para(X + 26, y, s_, RW - 26, 7.5, 1.45, fill="sub", fam=KR)
        y += 1.6
    zone("J4_06_SKILLS")
    yk = y + 1.4
    sec(yk, "SKILLS")
    t(X, yk + 10.6, FLOW, 7, "sub", 400, ls=0.1)
    cw = RW / 3
    for i, tool in enumerate(TOOLS):
        skill_h(X + (i % 3) * cw, yk + 14 + (i // 3) * 16.5, tool, rr=6.0, name_pt=8.3, small=7, line="")
    end_skills = yk + 14 + 16.5 + 12.5
    zone("J4_07_PORTFOLIO_LINK")
    yc = BOT - 13
    ln(X, yc, X + RW, yc, "line", 0.3)
    t(X, BOT, "PORTFOLIO", 10, "text", 600, ls=0.45)
    t(X + 32, BOT, "패션에 대한 안목은 포트폴리오에 — 별도 첨부", 7.5, "sub", 400, fam=KR)
    arrow(X + RW - 14, BOT - 1.2, "VIEW", 2.0, 6.5)
    zone("J4_08_FOLIO")
    t(X, FOLIO + 1.6, "JEONG HYEOKJU  ·  CV", 6, "sub", 500, ls=0.3)
    t(X + RW, FOLIO + 1.6, "JAJU  ·  ROUNDING VMD", 6, "sub", 500, "end", ls=0.3)
    zone_end()
    return end_skills, yc


def svg_text():
    bp.OUT.clear()
    w('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">')
    w('<title>CV · JAJU ROUNDING VMD · JEONG HYEOKJU</title>')
    theme(WHITE)
    fit = layout()
    w('</svg>')
    return "\n".join(bp.OUT), fit


class Doc(svg2idml.Doc):
    """new paragraph styles get a 'J4 ' prefix so they never collide with the form's existing ones."""

    def pstyle(self, font, style, size, lead, color, align, track):
        key = (font, style, round(size, 2), round(lead, 2), color, align, track)
        if key not in self.pstyles:
            self.pstyles[key] = f'J4 {len(self.pstyles) + 1:02d} {font} {style} {size:g}/{lead:g}'
        return self.pstyles[key]


def build(form, out, svg_path):
    zin = zipfile.ZipFile(form)
    files = {n: zin.read(n) for n in zin.namelist()}
    spread_name = next(n for n in files if n.startswith("Spreads/"))
    spread = files[spread_name].decode("utf-8")
    design = files["designmap.xml"].decode("utf-8")
    dom = re.search(r'DOMVersion="([^"]+)"', spread).group(1)
    layer = re.search(r'<Layer Self="([^"]+)"', design).group(1)
    # the form's photo frame (graphic frame with the placed image) — kept as is
    photo = re.search(r'<Rectangle Self="[^"]+"[^>]*ContentType="GraphicType".*?</Rectangle>', spread, re.S).group(0)
    old_stories = set(re.findall(r'ParentStory="([^"]+)"', spread))
    # new page items
    page = svg2idml.convert(svg_path)
    tmp = tempfile.mkdtemp()
    doc = Doc(210, 297, tmp)
    body = doc.page(page).replace('ItemLayer="uL"', f'ItemLayer="{layer}"')
    head = spread[:spread.index("</Page>") + len("</Page>")]
    spread_new = head + body + photo + "\n\t</Spread>\n</idPkg:Spread>"
    files[spread_name] = spread_new.encode("utf-8")
    # stories: drop the form's page stories, add the new ones
    for sid in old_stories:
        files.pop(f"Stories/Story_{sid}.xml", None)
        design = design.replace(f'<idPkg:Story src="Stories/Story_{sid}.xml" />', "").replace(f'<idPkg:Story src="Stories/Story_{sid}.xml"/>', "")
    for sid, xml in doc.stories:
        files[f"Stories/Story_{sid}.xml"] = xml.replace('DOMVersion="8.0"', f'DOMVersion="{dom}"').encode("utf-8")
    keep = [s for s in re.search(r'StoryList="([^"]*)"', design).group(1).split() if s not in old_stories]
    design = re.sub(r'StoryList="[^"]*"', f'StoryList="{" ".join(keep + [s for s, _ in doc.stories])}"', design, count=1)
    refs = "".join(f'<idPkg:Story src="Stories/Story_{s}.xml" />' for s, _ in doc.stories)
    i = design.rfind("</Document>")
    design = design[:i] + refs + design[i:]
    files["designmap.xml"] = design.encode("utf-8")
    # colours and paragraph styles the new items use
    graphic = files["Resources/Graphic.xml"].decode("utf-8")
    add = "".join(f'<Color Self="Color/{n}" Model="Process" Space="RGB" ColorValue="{c[0]} {c[1]} {c[2]}" ColorOverride="Normal" '
                  f'AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="{n}" ColorEditable="true" ColorRemovable="true" '
                  f'Visible="true" SwatchCreatorID="7937" />' for c, n in doc.colors.items() if f'Self="Color/{n}"' not in graphic)
    j = graphic.find("<Swatch ")
    graphic = graphic[:j] + add + graphic[j:]
    files["Resources/Graphic.xml"] = graphic.encode("utf-8")
    styles = files["Resources/Styles.xml"].decode("utf-8")
    just = {"left": "LeftAlign", "right": "RightAlign", "center": "CenterAlign"}
    ps = "".join(f'<ParagraphStyle Self="ParagraphStyle/{IW.q(n)}" Name="{IW.q(n)}" Imported="false" NextStyle="ParagraphStyle/{IW.q(n)}" '
                 f'KeyboardShortcut="0 0" FontStyle="{IW.q(s)}" PointSize="{size}" FillColor="{col}" Justification="{just[al]}" '
                 f'Hyphenation="false" Tracking="{tr}"><Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn>'
                 f'<PreviewColor type="enumeration">Nothing</PreviewColor><AppliedFont type="string">{IW.q(f)}</AppliedFont>'
                 f'<Leading type="unit">{lead}</Leading></Properties></ParagraphStyle>'
                 for (f, s, size, lead, col, al, tr), n in doc.pstyles.items())
    k = styles.find("</RootParagraphStyleGroup>")
    styles = styles[:k] + ps + styles[k:]
    files["Resources/Styles.xml"] = styles.encode("utf-8")
    # write: mimetype first, stored
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), files.pop("mimetype"), compress_type=zipfile.ZIP_STORED)
        for n, b in files.items():
            z.writestr(n, b, compress_type=zipfile.ZIP_DEFLATED)
    return len(doc.stories), len(old_stories)


def main(form, out):
    svg, (end_skills, link_line) = svg_text()
    assert end_skills <= link_line - 2, f"skills run into the portfolio line: {end_skills:.1f} > {link_line - 2:.1f}"
    svg_path = Path(out).with_suffix(".svg")
    svg_path.write_text(svg, encoding="utf-8")
    n_new, n_old = build(form, out, svg_path)
    print(f"wrote {out}: {n_new} text frames (form had {n_old}); skills end {end_skills:.1f} / link line {link_line:.1f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
