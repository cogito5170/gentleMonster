"""TYPE 1 hero: the name is replaced by a branding headline (ref (1) DVSY "DESIGN & FREEDOM").

    python3 docs/cv/blueprint/hero_options.py   # -> types/C-01.svg, hero_options.pdf

Six options, three two-word pairs and three sentences, drawn on the real hero (196 x 95 mm) at 58 %.
Every option comes from the applicant's own words; the source is printed under each panel.
"""
import subprocess
from pathlib import Path

from bp import *  # noqa: F401,F403
import bp

HERE = Path(__file__).parent

OPTIONS = [
    ("A1", ["RESTRAINT", "& BOLDNESS"], "절제와 과감",
     "자기소개서 문항 2: '건축에서 익힌 절제 위에 과감을 더해, 절제와 과감을 한 공간에서 함께 다루고자 합니다.'",
     "약점(과감)을 강점(절제)의 짝으로 세움. 자기소개서와 같은 말이라 두 장이 한 이야기가 됨."),
    ("A2", ["FRAME", "& INTERIOR"], "틀과 그 안",
     "자기소개서 문항 2 제목 '틀을 배우고, 그 안을 채우는 건축학도' · ① '그 틀 안의 실내 공간에 더 끌린다는 것을 알게 되었고'",
     "건축(틀)에서 공간 디자인(그 안)으로 옮겨 온 길을 두 단어로 보여 줌."),
    ("A3", ["ADVANCE", "& RECEDE"], "진출과 후퇴 (색)",
     "자기소개서 문항 2: '시선을 끄는 색과 한발 물러서는 색을 함께 다뤄' — 색채 용어 진출색 · 후퇴색",
     "디자인 감각을 색 이론의 말로. 오브제와 공간의 관계를 다루는 직무와 바로 이어짐."),
    ("B1", ["WHERE DID YOU", "LAST STOP?"], "어디에서 마지막으로 멈췄나요?",
     "포트폴리오 SPA 표지 문구 'Where Did You Last Stop?'",
     "CV와 포트폴리오가 같은 질문으로 시작 — 두 서류가 한 브랜드로 묶임."),
    ("B2", ["LEARN THE FRAME,", "FILL THE INSIDE."], "틀을 배우고, 그 안을 채운다",
     "자기소개서 문항 2 제목을 영어로 옮김",
     "자기소개서 제목과 같은 문장 — 첫 장과 둘째 장이 같은 문장으로 열림."),
    ("B3", ["AN ARCHITECT IS", "ALSO A DESIGNER."], "건축가도 디자이너",
     "맥락 전달 · 자기소개서 문항 2: '건축가도 디자이너라는 생각으로 시야를 넓혀 왔습니다.'",
     "건축 전공자가 디자이너 직무에 지원하는 이유를 한 문장으로."),
]

HW, HH = 196, 95          # hero size in A4 mm (TYPE 1)
MAXW = 150                # headline may not run past this
INDENT = 22               # second line indent = ref (1): '& FREEDOM' starts 11 % in


def fit(lines_, base=51, ls_em=0.031):
    pt = base
    while pt > 20:
        em = pt * PT
        widest = max(sum(0.66 if ch != " " else 0.28 for ch in s) * em + len(s) * ls_em * em for s in lines_)
        if widest + INDENT <= MAXW + INDENT * 0.2:
            return pt
        pt -= 1
    return pt


def hero(lines_):
    """TYPE 1 hero, origin at its top-left corner."""
    photo(0, 0, HW, HH, "PHOTO 01", "인물 사진 ____ (흑백 또는 저채도)", rx=1.6, at=(161, 11))
    pt = fit(lines_)
    em = pt * PT
    y1 = 55 if pt > 44 else 58
    t(8, y1, lines_[0], pt, "text", 100, ls=0.031 * em)
    t(8 + INDENT, y1 + em * 1.0, lines_[1], pt, "text", 100, ls=0.031 * em)
    t(9, 82.5, "SPATIAL DESIGNER  ·  공간 설계 디자이너  ·  JEONG HYEOKJU", 6.4, "text", 500, ls=0.2)
    t(9, 86.6, "건물을 설계하던 감각으로 매장을 설계하려는 건축학도", 5.6, "sub", 400, fam=KR)
    arrow(163, 85.5, "PAGE 2 · 자기소개서")
    return pt


def main():
    sheet_open()
    t(16, 17, "C-01   TYPE 1 · HERO HEADLINE  ·  6 OPTIONS", 10, INK, 700, ls=0.3)
    t(16, 22.5, "이름 자리를 작성자를 나타내는 말로 바꾼 안. 레퍼런스 ① DESIGN & FREEDOM 처럼 두 줄, 둘째 줄을 22 들여 씀 (① 은 11 %). "
                "첫 화면 196 × 95 를 58 % 로 그림.", 6.0, INK2, 400, fam=KR)
    s, gx, gy = 0.58, 16, 32
    pw, ph = HW * s, HH * s
    gap_x, cap_h = 14, 33
    for i, (code, lines_, ko, src, why) in enumerate(OPTIONS):
        col, row = i % 3, i // 3
        x = gx + col * (pw + gap_x)
        y = gy + row * (ph + cap_h + 14)
        theme(DARK)
        w(f'<g transform="translate({x},{y}) scale({s})">')
        pt = hero(lines_)
        w('</g>')
        cy = y + ph + 5
        t(x, cy, code, 8, INK, 700)
        t(x + 9, cy, " ".join(lines_), 7, INK, 600, ls=0.2)
        t(x + 9, cy + 4, ko, 5.8, INK2, 500, fam=KR)
        yy = para(x, cy + 9.5, "출처  " + src, pw, 5.2, 1.4, fill=INK, fam=KR)
        para(x, yy + 0.8, "읽힘  " + why, pw, 5.2, 1.4, fill=INK2, fam=KR)
        t(x + pw, cy, f"{pt}pt Thin", 5, INK2, 400, "end")
    # group labels in the left margin
    for row, lab in ((0, "A · 두 단어"), (1, "B · 문장")):
        y = gy + row * (ph + cap_h + 14) + ph / 2
        w(f'<text transform="translate({gx - 4},{y}) rotate(-90)" font-family="{KR}" font-size="{7 * PT}" font-weight="700" '
          f'fill="{INK}" text-anchor="middle">{lab}</text>')
    yb = gy + 2 * (ph + cap_h + 14) - 4
    ln(16, yb, 404, yb, RULE, 0.3)
    notes = ["· 이름 JEONG HYEOKJU 는 메뉴 왼쪽 로고와 첫 화면 작은 줄에 남음 — 헤드라인이 이름을 대신해도 누구의 CV인지 보임.",
             "· 글자 크기는 줄이 150 을 넘지 않게 맞춤 (레퍼런스 ① 의 헤드라인이 첫 화면 폭의 약 60 %).",
             "· 고를 때 둘을 섞어도 됨: 예) 헤드라인 A1 + 작은 줄에 B1 질문."]
    lines(16, yb + 5, notes, 5.8, 1.5, fill=INK, fam=KR)
    path = HERE / "types" / "C-01.svg"
    sheet_close(path)
    subprocess.run(["inkscape", str(path), "--export-type=pdf", f"--export-filename={HERE / 'hero_options.pdf'}"],
                   check=True, capture_output=True)
    print(HERE / "hero_options.pdf")


if __name__ == "__main__":
    main()
