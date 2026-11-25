"""Blue Elephant CV -> Gentle Monster 공간 오브제 디자이너: proposal sheet (PDF) + Markdown.

    python3 docs/cv/blueprint/gm_object_changes.py   # -> docs/cv/gentle_monster_object/GM_OBJECT_CV_proposal.pdf / .md

Posting: company analysis K0 (claude/gracious-edison-inoq0z:docs/company_analysis/gentle_monster/01_scope_posting.md, 2026-11-17).
'Now' column = the Blue Elephant CV text (apply_blue_elephant.jsx, the latest adopted lines).
Proposed text comes only from the applicant's own finished writing: GM 공간 설계 디자이너 cover letter Q2 (selection.json),
the JAJU / Blue Elephant cover-letter finals, and the GM CV the applicant completed. Lengths stay close so the layout holds.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bp  # noqa: E402
from bp import *  # noqa: F401,F403,E402
from page2 import kwrap  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "gentle_monster_object"

# posting -> where the CV answers it
POSTING = [
    ("담당업무", "오브제팀 — 오브제 디자인 · 제작 중점", "직무 줄 · 한 줄 소개 · PROFILE 3 · KEYWORDS 04 · 경력의 실물 모형"),
    ("담당업무", "공간 요소 (레이아웃 · 마감재 · 가구)", "INTERESTS (가구와 조명 · 마감재) · 카페 테이블 재배치"),
    ("자격요건", "발상 (기획력)", "KEYWORDS 01 기획"),
    ("자격요건", "미학 · 컬러에 대한 감도", "KEYWORDS 02 컬러 감도"),
    ("자격요건", "패션과 문화에 대한 관심 · 패션 관점의 감각", "PROFILE 1 · KEYWORDS 03 · INTERESTS 패션"),
    ("우대사항", "3D Tool 사용 역량", "KEYWORDS 04 · SKILLS (그대로)"),
    ("우대사항", "새로움을 찾는 즐거움 · 배우려는 의지", "FIVE VISION 03 도전 (그대로)"),
    ("기타", "병역 마친 분", "학력의 '육군 병장 만기 전역' (그대로) — 공고 조건을 이력서가 이미 보여 줌"),
]

# (zone, place, now (Blue Elephant), proposal (GM object), posting reason, fact source)
CHANGES = [
    ("사이드바", "직무 줄 1", "CREATIVE INTERN", "SPACE OBJECT DESIGNER", "공고 제목 '공간 오브제 디자이너'", "—"),
    ("사이드바", "직무 줄 2", "블루엘리펀트 콘텐츠 디자인 인턴", "젠틀몬스터 공간 오브제 디자이너", "공고 제목", "—"),
    ("사이드바", "한 줄 소개", "레퍼런스에서 찾은 아이디어를 이미지로 옮기려는 지원자",
     "오브제가 공간 속에서 하나의 장면이 되게 하려는 지원자", "담당업무 '오브제 디자인 중점'",
     "GM 문항 2 '오브제가 공간 속에서 하나의 장면이 되게 하는 방식에 관심이 많습니다'"),
    ("ABOUT", "제목 (2줄)", "리서치로 생각하고, / 시각화로 먼저 확인하는 디자이너", "틀을 배우고, / 그 안을 채우는 건축학도",
     "팀소개 '스토어 · 팝업 기획부터 오픈까지' — 틀(건축) 안을 채우는 일", "GM 문항 2 제목"),
    ("ABOUT", "오른쪽 메모", "자기소개서 2번", "자기소개서 2번", "—", "젠틀몬스터 지원서 문항 번호에 맞춰 (문항 확인 필요)"),
    ("ABOUT", "PROFILE 1", "건축을 공부하며 파사드 디자인에 관심", "옷에 대한 관심은 건축보다 먼저", "자격 '패션과 문화에 대한 관심'",
     "JAJU 1번 확정본"),
    ("ABOUT", "PROFILE 2", "포토샵 · 일러스트 · 렌더링으로 시각화", "건축으로 공간의 크기와 거리를 가늠하는 감각", "오브제 = 공간 속 크기와 거리",
     "JAJU 1번 확정본"),
    ("ABOUT", "PROFILE 3", "고객이 매장과 화면에서 처음 만나는 이미지를 목표로", "아트 오브제와 가구, 마감재 기획을 목표로",
     "담당업무 '오브제 · 가구 · 마감재'", "GM 문항 2 '이 감각을 아트 오브제와 가구, 마감재를 기획하는 데 쓰겠습니다'"),
    ("ABOUT", "INTERESTS 1", "사진 · 패션", "패션 · 공간", "자격 '패션 관점의 감각'", "젠틀몬스터 CV (사용자 완성본)"),
    ("ABOUT", "INTERESTS 2", "파사드 디자인", "가구와 조명 수집", "담당업무 '가구'", "젠틀몬스터 CV · GM 맥락 '가구와 조명을 계속 사 모음'"),
    ("ABOUT", "INTERESTS 3", "해외 레퍼런스 리서치", "실내 마감재와 마감 방식", "담당업무 '마감재'", "젠틀몬스터 CV '건축물의 실내 마감재와 마감 방식'"),
    ("KEYWORDS", "01 제목", "기획력", "기획", "자격 '발상 (기획력)'", "GM 문항 2 '첫째, 기획입니다'"),
    ("KEYWORDS", "01 설명", "리서치로 컨셉을 세우고, 해외 자료를 하나의 컨셉으로 묶어 정리합니다",
     "리서치와 분석으로 컨셉을 세우고, 하나의 생각을 끝까지 형태로 밀고 갑니다", "자격 '발상 (기획력)'",
     "GM 문항 2 '리서치와 분석으로 컨셉을 세우고 … 하나의 생각을 끝까지 형태로 밀고 가는'"),
    ("KEYWORDS", "02 제목", "미리 확인", "컬러 감도", "자격 '컬러에 대한 감도'", "GM 문항 2 셋째 강점"),
    ("KEYWORDS", "02 설명", "만들기 전에 렌더링과 후보정으로 재료와 색을 미리 확인합니다",
     "원색 대신 채도를 낮춘 색으로 포인트를 주고 주변과 어우러지게 합니다", "자격 '미학 · 컬러에 대한 감도'",
     "GM 문항 2 '원색 대신 채도를 낮춘 색으로 포인트를 주고 주변과 어우러지게 해'"),
    ("KEYWORDS", "03 제목", "이미지 작업", "패션에 대한 안목", "자격 '패션 관점에서 특별한 감각'", "JAJU 1번 확정본"),
    ("KEYWORDS", "03 설명", "포토샵 · 일러스트 · 인디자인으로 시각화와 후보정, AI 툴도 적극 활용",
     "스타일을 가리지 않고 입어 보며 기른 안목 — 원단 · 디자인 · 색감", "자격 '세련된 취향'",
     "JAJU 1번 · 2번 확정본 (지난 자주 이력서의 KEYWORDS 03)"),
    ("KEYWORDS", "04 제목", "사진과 패션", "구상을 미리 확인", "우대 '3D Tool' · 담당업무 '제작'", "JAJU 2번 확정본"),
    ("KEYWORDS", "04 설명", "평소 찍은 사진과 패션 사진을 개인 SNS에 올립니다",
     "만들기 전에 3D로 먼저 구현해 크기와 배치를 확인합니다", "우대 '3D Tool' · '오브제 제작 경험 (없어도 됨)'",
     "JAJU 2번 · BE 2번 '3D로 먼저 구현해 크기와 배치를 확인' (사용자 확인 10-25)"),
    ("EDUCATION", "마지막 줄", "2026.11  블루엘리펀트 인턴 지원", "2026.11  젠틀몬스터 공간 오브제 디자이너 지원", "—",
     "젠틀몬스터 지원서에 블루엘리펀트를 쓰지 않음 (기업 분석 K1 · 10-13 결정)"),
    ("EXPERIENCE", "인턴 설명 순서", "1) 현장 실측 · 모델링 …  2) 실물 모형 제작 → 《돌봄의 디자인》 전시",
     "1) 실물 모형 제작 → 《돌봄의 디자인》 전시  2) 현장 실측 · 모델링 …", "담당업무 '오브제 제작' — 만든 경험을 먼저",
     "JAJU 2번 확정본 (두 줄을 바꿔 놓기만, 글은 그대로)"),
]
KEEP = ["이름 · 사진 · 연락처", "FIVE VISION 다섯 줄 — 03 '새로운 일을 주저 없이 하는 도전'이 우대 '새로움을 찾는 즐거움'과 맞음",
        "NUMBERS (5 · 7 · 6 · 1) — 6 TOOLS '2D-3D 구현'이 우대 '3D Tool'과 맞음", "학력 1–5행 (병역 · 학교)",
        "경력: 카페 아르바이트 (테이블 · 식물 재배치 = 공간 요소)", "SKILLS 툴 6종과 흐름 줄"]
CHECK = ["블루엘리펀트가 남은 곳이 없게: 직무 줄 · 학력 마지막 줄 (위 표) — 경력에 'PROTEAN' 을 더했다면 그 항목도 뺌",
         "자기소개서 문항 번호 — 젠틀몬스터 입사지원서 문항이 지난번과 같은지 (기업 분석 UQ1)",
         "오브제 · 가구를 직접 만든 경험이 더 있으면 경력에 (UQ2) — 지금 근거는 인턴 실물 모형 하나",
         "선택: 지난 젠틀몬스터 CV 의 '아이웨어 브랜드(젠틀몬스터) · 직원 COMMING SOON' 줄 — 쓰면 한 줄이 늘어 레이아웃이 바뀜",
         "선택: ABOUT 제목을 지난 젠틀몬스터 CV 의 헤드라인 'FRAME & INTERIOR' 로 — 같은 뜻의 영문"]


def sheet(path):
    W, H, M = 297, 210, 12
    pt, lh = 6.0, 6.0 * PT * 1.42
    pages = []

    def head(sub=True):
        bp.OUT.clear()
        w(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">')
        r(0, 0, W, H, "#FFFFFF")
        t(M, 16, "블루엘리펀트 이력서 → 젠틀몬스터 공간 오브제 디자이너 · 수정 제안", 12, INK, 700, fam=KR)
        if sub:
            t(M, 21.5, "기준: 기업 분석 K0 모집요강 (2026-11-17). 제안 글은 혁주님이 이미 쓴 글(젠틀몬스터 문항 2 · 자주 · 블루엘리펀트 확정본 · 젠틀몬스터 CV)에서만. "
                       "글자 수는 지금 칸과 비슷하게.", 6.0, INK2, 400, fam=KR)

    # page 1: posting map + first rows
    head()
    t(M, 31, "1  모집요강 → 이력서에서 답하는 자리", 8, INK, 700, fam=KR)
    pc = [(M, 20), (M + 20, 78), (M + 98, 175)]
    y = 37
    for (x, wd), h in zip(pc, ["항목", "모집요강", "이력서 자리 (제안 반영 후)"]):
        t(x, y, h, 6.4, INK, 700, fam=KR)
    ln(M, y + 1.6, W - M, y + 1.6, INK, 0.3)
    y += 5.6
    for a, b, c in POSTING:
        t(pc[0][0], y, a, pt, INK2, 400, fam=KR); t(pc[1][0], y, b, pt, INK, 700, fam=KR); t(pc[2][0], y, c, pt, INK, 400, fam=KR)
        y += lh + 1.5
        ln(M, y - 3.0, W - M, y - 3.0, RULE, 0.2)
    y += 5
    t(M, y, "2  바꿀 글", 8, INK, 700, fam=KR)
    cols = [(M, 17), (M + 17, 22), (M + 39, 60), (M + 99, 66), (M + 165, 50), (M + 215, 58)]
    heads = ["구역", "자리", "지금 (블루엘리펀트)", "제안 (젠틀몬스터 공간 오브제)", "공고 근거", "글의 출처"]

    def table_head(y):
        for (x, _), h in zip(cols, heads):
            t(x, y, h, 6.4, INK, 700, fam=KR)
        ln(M, y + 1.6, W - M, y + 1.6, INK, 0.3)
        return y + 5.6
    y = table_head(y + 6)
    for z, place, now, new, why, src in CHANGES:
        cells = [z, f"{place}  ({len(now)}→{len(new)}자)" if now not in ("—",) and len(now) < 60 else place, now, new, why, src]
        wrapped = [kwrap(cell, wd - 2.2, pt) for (x, wd), cell in zip(cols, cells)]
        hrow = max(len(c) for c in wrapped) * lh + 2.2
        if y + hrow > H - 12:
            w('</svg>'); pages.append("\n".join(bp.OUT)); head(False); y = table_head(28)
        for i, ((x, wd), ls) in enumerate(zip(cols, wrapped)):
            fill = {2: INK2, 3: RED, 4: INK, 5: INK2}.get(i, INK)
            weight = 700 if i in (0, 3) else 400
            for j, s in enumerate(ls):
                t(x, y + j * lh, s, pt, fill, weight, fam=KR)
        y += hrow
        ln(M, y - 3.0, W - M, y - 3.0, RULE, 0.2)
    if y + 42 > H - 10:
        w('</svg>'); pages.append("\n".join(bp.OUT)); head(False); y = 30
    y += 4
    t(M, y, "그대로 둔 것", 7, INK, 700, fam=KR)
    t(M + 140, y, "확인해 주실 것", 7, RED, 700, fam=KR)
    yy = y + 4.4
    for s in KEEP:
        for part in kwrap("· " + s, 132, pt):
            t(M, yy, part, pt, INK, 400, fam=KR); yy += lh
        yy += 0.5
    yy = y + 4.4
    for s in CHECK:
        for part in kwrap("· " + s, 133, pt):
            t(M + 140, yy, part, pt, INK, 400, fam=KR); yy += lh
        yy += 0.5
    w('</svg>'); pages.append("\n".join(bp.OUT))
    pdfs = []
    for i, svg in enumerate(pages, 1):
        p = OUT / f"_p{i}.svg"
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
    md = ["# 블루엘리펀트 이력서 → 젠틀몬스터 공간 오브제 디자이너 · 수정 제안", "",
          "기준: 기업 분석 K0 모집요강 (`claude/gracious-edison-inoq0z:docs/company_analysis/gentle_monster/01_scope_posting.md`). "
          "제안 글은 혁주님이 이미 쓴 글에서만 가져옴.", "", "## 모집요강 → 이력서 자리", "",
          "| 항목 | 모집요강 | 이력서 자리 |", "|---|---|---|"]
    md += [f"| {a} | {b} | {c} |" for a, b, c in POSTING]
    md += ["", "## 바꿀 글", "", "| 구역 | 자리 | 지금 (블루엘리펀트) | 제안 (젠틀몬스터 공간 오브제) | 공고 근거 | 글의 출처 |", "|---|---|---|---|---|---|"]
    md += [f"| {z} | {p} | {n} | **{b}** | {y} | {s} |" for z, p, n, b, y, s in CHANGES]
    md += ["", "## 그대로 둔 것", ""] + [f"- {s}" for s in KEEP] + ["", "## 확인해 주실 것", ""] + [f"- {s}" for s in CHECK]
    path.write_text("\n".join(md) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    n = sheet(OUT / "GM_OBJECT_CV_proposal.pdf")
    markdown(OUT / "GM_OBJECT_CV_proposal.md")
    print(OUT / "GM_OBJECT_CV_proposal.pdf", n, "page(s)")


if __name__ == "__main__":
    main()
