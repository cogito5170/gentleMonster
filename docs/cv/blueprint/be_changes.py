"""JAJU CV -> Blue Elephant Creative Intern: the changed text, as a PDF change sheet and a Markdown text file.

    python3 docs/cv/blueprint/be_changes.py   # -> docs/cv/blue_elephant/BE_CV_changes.pdf / .md

Base: the applicant's latest JAJU CV (PDF uploaded 2026-11-05). Source of the new text: Blue Elephant cover letter
finals on claude/clever-knuth-1dezlo (q1_FINAL 2026-11-04, q2_FINAL 2026-11-05, Q3 v6 = the Word file 2026-11-05).
Only what the letters say is used; anything not in them stays as it is or is flagged.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bp  # noqa: E402
from bp import *  # noqa: F401,F403,E402
from page2 import kwrap  # noqa: E402  (real Noto Sans KR line breaks)

OUT = Path(__file__).resolve().parent.parent / "blue_elephant"

# (zone, place, now (JAJU), new (Blue Elephant), source)
CHANGES = [
    ("사이드바", "직무 줄 1", "ROUNDING VMD", "CREATIVE INTERN", "공고 제목 'Creative Intern'"),
    ("사이드바", "직무 줄 2", "JAJU 라운딩 VMD 지원", "블루엘리펀트 비주얼 콘텐츠 디자인 인턴 지원", "공고 제목 '(비주얼 콘텐츠 디자인 인턴)'"),
    ("사이드바", "한 줄 소개", "건축에서 배운 공간감과 패션에 대한 안목을 접목하려는 지원자",
     "시각화 작업을 매장과 화면의 이미지로 옮기려는 지원자",
     "1번 '학부에서 흥미를 느낀 시각화 작업을, 고객이 매장과 화면에서 보는 이미지로 옮기고 싶습니다'"),
    ("ABOUT", "오른쪽 메모", "자기소개서 1번", "자기소개서 1 · 2번", "제목을 2번 소제목으로 바꿔서"),
    ("ABOUT", "제목 (2줄)", "일상의 불편에서 / 진열의 가능성을 찾다", "리서치로 생각하고, / 시각화로 먼저 확인하는 디자이너", "2번 소제목 그대로"),
    ("ABOUT", "PROFILE 1", "옷에 대한 관심은 건축보다 먼저", "건축을 공부하며 파사드 디자인에 관심", "1번 '건축을 공부하면서도 파사드 디자인에 관심을 가져 왔습니다'"),
    ("ABOUT", "PROFILE 2", "건축으로 공간의 크기와 거리를 가늠하는 감각", "설계 수업에서 포토샵 · 일러스트 · 렌더링으로 시각화",
     "1번 '생각과 개념, 결과물을 포토샵과 일러스트, 렌더링 작업으로 시각화'"),
    ("ABOUT", "PROFILE 3", "옷과 매장이 어떻게 보일지 기획하는 VMD를 목표로", "고객이 매장과 화면에서 처음 만나는 이미지를 목표로",
     "1번 '고객이 매장과 화면에서 처음 만나는 이미지를 만드는 자리'"),
    ("ABOUT", "INTERESTS 1", "패션 · 공간", "사진 · 패션", "1번 '사진과 패션에 대한 관심'"),
    ("ABOUT", "INTERESTS 2", "가구와 조명", "파사드 디자인", "1번 '파사드 디자인에 관심'"),
    ("ABOUT", "INTERESTS 3", "물건의 배치 방식", "해외 레퍼런스 리서치", "1번 '해외 레퍼런스 찾기에도 익숙합니다'"),
    ("KEYWORDS", "01 제목", "일상의 불편", "기획력", "2번 '첫째, 리서치로 컨셉을 세우는 기획력'"),
    ("KEYWORDS", "01 설명", "일상의 작은 불편을 먼저 알아채고, 있는 것에서 바꿀 가능성을 찾습니다",
     "리서치로 컨셉을 세우고, 해외 자료를 하나의 컨셉으로 묶어 정리합니다", "2번 첫째 문단"),
    ("KEYWORDS", "02 제목", "공간감", "미리 확인", "2번 '둘째, 만들기 전에 시각화로 미리 확인하는 능력'"),
    ("KEYWORDS", "02 설명", "상품 하나보다 매장 전체의 흐름 안에서 자리를 봅니다",
     "만들기 전에 렌더링과 후보정으로 재료와 색을 미리 확인합니다", "2번 둘째 문단"),
    ("KEYWORDS", "03 제목", "패션에 대한 안목", "이미지 작업", "1번 '하나는 이미지 작업으로'"),
    ("KEYWORDS", "03 설명", "스타일을 가리지 않고 입어 보며 기른 안목 — 원단 · 디자인 · 색감",
     "포토샵 · 일러스트 · 인디자인으로 시각화와 후보정, AI 툴도 적극 활용", "1번 셋째 문단"),
    ("KEYWORDS", "04 제목", "구상을 미리 확인", "사진과 패션", "1번 '다른 하나는 사진과 패션에 대한 관심'"),
    ("KEYWORDS", "04 설명", "진열을 바꾸기 전에 배치를 3D로 미리 그려 확인합니다",
     "평소 찍은 사진과 패션 사진을 개인 SNS에 올립니다", "1번 셋째 문단"),
    ("EDUCATION", "마지막 줄", "2026.10  JAJU 라운딩 VMD 지원", "2026.11  블루엘리펀트 Creative Intern 지원", "지원 시점 — 날짜 확인 필요"),
    ("EXPERIENCE", "새 항목 · 제목 (맨 위)", "—", "2026  포트폴리오 'PROTEAN' · 개인 작업", "3번 (v6) — 기간이 없어 '2026'만"),
    ("EXPERIENCE", "새 항목 · 설명 1", "—", "썸네일 · 웹페이지 · 파사드 · SNS 피드 제작", "3번 '썸네일과 웹페이지, 파사드, SNS까지 여러 형식의 작업'"),
    ("EXPERIENCE", "새 항목 · 설명 2", "—", "AI → 포토샵 · 일러스트 → 인디자인으로 툴을 연결해 제작",
     "3번 'AI로 만든 이미지를 포토샵과 일러스트로 다듬어 인디자인으로 엮는 식으로 툴을 연결해 썼습니다'"),
]
KEEP = ["이름 · 사진 · 연락처", "FIVE VISION 다섯 줄 (회사와 무관한 태도)", "NUMBERS (5 · 7 · 6 · 1)",
        "학력 1–5행", "경력: 건축사사무소 (a.co.lab) 인턴 · 카페 아르바이트 (사실 그대로)", "SKILLS 툴 6종과 흐름 줄"]
CHECK = ["인턴 기간이 '2026.08 – 08'로 되어 있습니다 — 한 달이면 '2026.08', 아니면 끝 달 확인",
         "EDUCATION 마지막 줄의 날짜 '2026.11' — 실제 지원 날짜로",
         "PROTEAN 작업 기간 — 자기소개서에 없어 '2026'만 적음",
         "선택: 공고 우대사항(AI 툴 활용)에 맞춰 SKILLS 흐름 줄에 AI 를 더할지 (예: AI → RETOUCH → …) — 툴 이름은 자기소개서에 없어 넣지 않음"]


def sheet(path):
    """A4 landscape change sheet; returns page SVG strings (paginated)."""
    W, H, M = 297, 210, 12
    cols = [(M, 22), (M + 22, 26), (M + 48, 74), (M + 122, 88), (M + 210, 63)]
    pt, lh = 6.4, 6.4 * PT * 1.42
    pages, y = [], None

    def new_page(head):
        bp.OUT.clear()
        w(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">')
        r(0, 0, W, H, "#FFFFFF")
        t(M, 16, "JAJU 이력서 → 블루엘리펀트 Creative Intern · 바뀐 부분", 12, INK, 700, fam=KR)
        t(M, 21.5, "근거: 블루엘리펀트 자기소개서 확정본 (1번 11/04 · 2번 11/05 · 3번 v6 11/05, Word 파일과 같은 판). 자기소개서에 없는 사실은 넣지 않음.",
          6.2, INK2, 400, fam=KR)
        if not head:
            return 30
        heads = ["구역", "자리", "지금 (JAJU)", "바꿀 글 (블루엘리펀트)", "근거"]
        for (x, _), h in zip(cols, heads):
            t(x, 30, h, 6.8, INK, 700, fam=KR)
        ln(M, 32, W - M, 32, INK, 0.35)
        return 36.5

    y = new_page(True)
    for zone, place, now, new, src in CHANGES:
        cells = [zone, place, now, new, src]
        wrapped = [kwrap(c, wd - 2.5, pt) for (x, wd), c in zip(cols, cells)]
        hrow = max(len(c) for c in wrapped) * lh + 2.6
        if y + hrow > H - 16:
            w('</svg>'); pages.append("\n".join(bp.OUT)); y = new_page(False)
        for i, ((x, wd), ls) in enumerate(zip(cols, wrapped)):
            fill = INK2 if i == 2 else RED if i == 3 else INK2 if i == 4 else INK
            weight = 700 if i in (0, 3) else 400
            for j, s in enumerate(ls):
                t(x, y + j * lh, s, pt, fill, weight, fam=KR)
        y += hrow
        ln(M, y - 3.4, W - M, y - 3.4, RULE, 0.2)
    # keep / check
    if y + 40 > H - 10:
        w('</svg>'); pages.append("\n".join(bp.OUT)); y = new_page(False) - 3
    y += 3
    t(M, y, "그대로 둔 것", 7.2, INK, 700, fam=KR)
    t(M + 150, y, "확인해 주실 것", 7.2, RED, 700, fam=KR)
    yy = y + 4.6
    for s in KEEP:
        t(M, yy, "· " + s, pt, INK, 400, fam=KR); yy += lh + 0.6
    yy = y + 4.6
    for s in CHECK:
        for k, part in enumerate(kwrap("· " + s, 123, pt)):
            t(M + 150, yy, part, pt, INK, 400, fam=KR); yy += lh
        yy += 0.6
    w('</svg>'); pages.append("\n".join(bp.OUT))
    pdfs = []
    for i, svg in enumerate(pages, 1):
        p = OUT / f"_sheet_{i}.svg"
        p.write_text(svg, encoding="utf-8")
        pdf = p.with_suffix(".pdf")
        subprocess.run(["inkscape", str(p), "--export-type=pdf", f"--export-filename={pdf}"], check=True, capture_output=True)
        pdfs.append(str(pdf)); p.unlink()
    if len(pdfs) > 1:
        subprocess.run(["pdfunite", *pdfs, str(path)], check=True)
        for f in pdfs:
            Path(f).unlink()
    else:
        Path(pdfs[0]).replace(path)
    return len(pages)


def markdown(path):
    md = ["# JAJU 이력서 → 블루엘리펀트 Creative Intern · 바뀐 부분", "",
          "근거: 블루엘리펀트 자기소개서 확정본 — 1번 `blue_elephant_q1_FINAL.md`(2026-11-04), 2번 `blue_elephant_q2_FINAL.md`(2026-11-05), "
          "3번 v6(`blue_elephant_Q1-3.docx`, 2026-11-05). 바탕: 2026-11-05에 올려 주신 자주 이력서 PDF.", "",
          "| 구역 | 자리 | 지금 (JAJU) | 바꿀 글 (블루엘리펀트) | 근거 |", "|---|---|---|---|---|"]
    md += [f"| {z} | {p} | {n} | **{b}** | {s} |" for z, p, n, b, s in CHANGES]
    md += ["", "## 붙여 넣기용 (위에서 아래 순서)", ""]
    last = None
    for z, p, n, b, s in CHANGES:
        if z != last:
            md += ["", f"### {z}"]
            last = z
        md.append(f"- {p}: {b}")
    md += ["", "## 그대로 둔 것", ""] + [f"- {s}" for s in KEEP]
    md += ["", "## 확인해 주실 것", ""] + [f"- {s}" for s in CHECK]
    path.write_text("\n".join(md) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    n = sheet(OUT / "BE_CV_changes.pdf")
    markdown(OUT / "BE_CV_changes.md")
    print(OUT / "BE_CV_changes.pdf", n, "page(s)"); print(OUT / "BE_CV_changes.md")


if __name__ == "__main__":
    main()
