"""TYPE 1 hero headline as two words (WORD & WORD, ref (1) DESIGN & FREEDOM): nine options in three axes.

    python3 docs/cv/blueprint/hero_words.py   # -> types/C-02.svg, hero_words.pdf

Every pair comes from the applicant's own words; the source is printed under each panel.
"""
import subprocess
from pathlib import Path

from bp import *  # noqa: F401,F403
from hero_options import HH, HW, hero

HERE = Path(__file__).parent

AXES = [
    ("1 · 사람", "어떤 사람인가", [
        ("W1", ["RESTRAINT", "& BOLDNESS"], "절제와 과감",
         "자기소개서 문항 2: '건축에서 익힌 절제 위에 과감을 더해, 절제와 과감을 한 공간에서 함께 다루고자 합니다.'",
         "약점(과감)을 강점(절제)의 짝으로 세움. 자기소개서와 같은 말."),
        ("W2", ["ARCHITECT", "& DESIGNER"], "건축가이자 디자이너",
         "자기소개서 문항 2: '건축가도 디자이너라는 생각으로 시야를 넓혀 왔습니다.'",
         "건축 전공자가 디자이너 직무에 지원하는 이유가 두 단어에 담김. 주의: 아직 학생이라 ARCHITECT 가 과하게 읽힐 수 있음."),
        ("W3", ["STYLE", "& ARCHITECTURE"], "스타일과 건축",
         "포트폴리오 SPA (STYLE · PICTURE · ARCHITECTURE) · MY STYLE '헤어 · 옷의 톤 · 향을 그날 갈 장소에 맞춘다'",
         "패션 브랜드에 지원하는 건축학도 — 공고의 '패션과 문화에 대한 관심'과 맞닿음."),
    ]),
    ("2 · 공간", "무엇을 디자인하나", [
        ("W4", ["FRAME", "& INTERIOR"], "틀과 그 안",
         "자기소개서 문항 2 제목 '틀을 배우고, 그 안을 채우는 건축학도' · '그 틀 안의 실내 공간에 더 끌린다는 것을 알게 되었고'",
         "건축(틀)에서 공간 디자인(그 안)으로 옮겨 온 길."),
        ("W5", ["OBJECT", "& SPACE"], "오브제와 공간",
         "자기소개서 문항 2: '강렬한 오브제일수록 색채의 강약이 공간과의 관계를 정한다고 생각합니다.'",
         "공고의 '아트 오브제 · 가구 · 마감재 기획'과 바로 이어짐."),
        ("W6", ["PAUSE", "& MEMORY"], "멈춤과 기억",
         "자기소개서 문항 1 축 문장 '이용자가 멈추고, 이끌리고, 그 경험을 기억하는 공간' (보류 중) · 포트폴리오 동사 '멈춘다'",
         "포트폴리오와 같은 동사. 문항 1이 정해지면 그 글과도 이어짐."),
    ]),
    ("3 · 방법", "어떻게 만드나", [
        ("W7", ["CONCEPT", "& FORM"], "컨셉과 형태",
         "자기소개서 문항 2: '컨셉을 세우고 그 컨셉을 건물로 발전시켰습니다. 하나의 생각을 끝까지 형태로 밀고 가는'",
         "강점 첫째(기획)와 둘째(구현)를 한 쌍으로."),
        ("W8", ["PROPORTION", "& COLOR"], "비례와 색",
         "자기소개서 문항 2: '건물의 비례, 이미지 표현, 색채를 다듬는 작업' · '절제된 비례와 색 조합에는 익숙합니다'",
         "자신 있다고 말한 두 가지를 그대로."),
        ("W9", ["ADVANCE", "& RECEDE"], "진출과 후퇴 (색)",
         "자기소개서 문항 2: '시선을 끄는 색과 한발 물러서는 색을 함께 다뤄' — 색채 용어 진출색 · 후퇴색",
         "디자인 감각을 색 이론의 말로."),
    ]),
]


def main():
    sheet_open()
    t(16, 17, "C-02   TYPE 1 · HERO HEADLINE  ·  WORD & WORD  ·  9 OPTIONS", 10, INK, 700, ls=0.3)
    t(16, 22.5, "이름 자리를 작성자를 나타내는 두 단어로. 세 갈래(사람 · 공간 · 방법) × 3. 레퍼런스 ① 처럼 두 줄, 둘째 줄 22 들임. "
                "첫 화면 196 × 95 를 50 % 로 그림.", 6.0, INK2, 400, fam=KR)
    s, gx, gy = 0.50, 26, 32
    pw, ph = HW * s, HH * s
    gap_x, pitch = 16, ph + 31
    for row, (axis, q, opts) in enumerate(AXES):
        y = gy + row * pitch
        w(f'<text transform="translate({gx - 9},{y + ph / 2}) rotate(-90)" font-family="{KR}" font-size="{7.4 * PT}" '
          f'font-weight="700" fill="{INK}" text-anchor="middle">{axis}</text>')
        w(f'<text transform="translate({gx - 5},{y + ph / 2}) rotate(-90)" font-family="{KR}" font-size="{5.4 * PT}" '
          f'fill="{INK2}" text-anchor="middle">{q}</text>')
        for col, (code, lines_, ko, src, why) in enumerate(opts):
            x = gx + col * (pw + gap_x)
            theme(DARK)
            w(f'<g transform="translate({x},{y}) scale({s})">')
            pt = hero(lines_)
            w('</g>')
            cy = y + ph + 4.6
            t(x, cy, code, 7.4, INK, 700)
            t(x + 9, cy, " ".join(lines_), 6.6, INK, 600, ls=0.2)
            t(x + pw, cy, f"{pt}pt Thin", 4.8, INK2, 400, "end")
            t(x + 9, cy + 3.8, ko, 5.6, INK2, 500, fam=KR)
            yy = para(x, cy + 8.4, "출처  " + src, pw, 5.0, 1.35, fill=INK, fam=KR)
            para(x, yy + 0.6, "읽힘  " + why, pw, 5.0, 1.35, fill=INK2, fam=KR)
    # right column: how to choose
    RX = gx + 3 * pw + 2 * gap_x + 12
    ln(RX - 6, 30, RX - 6, 287, INK, 0.3)
    t(RX, 37, "HOW TO PICK", 8, INK, 700, ls=0.3)
    guide = [("1 · 사람", "누구인지를 먼저 말함. 이름 대신 정체성."),
             ("2 · 공간", "무엇을 만들고 싶은지. 직무(스토어 · 팝업 · 오브제)와 가까움."),
             ("3 · 방법", "어떻게 만드는지. 감각과 기술을 앞에 둠.")]
    y = 44
    for k, v in guide:
        t(RX, y, k, 6, INK, 700, fam=KR)
        y = para(RX, y + 3.6, v, 50, 5.4, 1.4, fill=INK2, fam=KR) + 3
    t(RX, y + 4, "공통", 6, INK, 700, fam=KR)
    notes = ["두 단어 모두 혁주님 원고에 있는 말 — 지어낸 표현 없음.",
             "이름 JEONG HYEOKJU 는 메뉴 로고와 첫 화면 작은 줄에 남음.",
             "글자 크기는 둘째 줄이 150 을 넘지 않게 맞춤 (51pt 기준, 긴 단어는 줄임).",
             "W1 · W4 · W9 는 앞서 보낸 C-01 의 A1 · A2 · A3."]
    y += 7.6
    for s_ in notes:
        y = para(RX, y, "· " + s_, 50, 5.4, 1.4, fill=INK, fam=KR) + 1.5
    path = HERE / "types" / "C-02.svg"
    sheet_close(path)
    subprocess.run(["inkscape", str(path), "--export-type=pdf", f"--export-filename={HERE / 'hero_words.pdf'}"],
                   check=True, capture_output=True)
    print(HERE / "hero_words.pdf")


if __name__ == "__main__":
    main()
