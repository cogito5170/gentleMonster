# Gentle Monster 편집 시스템 — 첫 수직 기능

브리프 한 줄 → 연구 원장 → Drift → 방향 ≥ 3 → 편집 계획 → HTML + PDF → QA.
모델 호출 없이 돈다(약 4초, Chromium 포함).

```bash
python3 -m gentle_monster magazine "Gentle Monster의 브랜드 세계관을 중심으로, 미래의 유물과 인간의 감각을 주제로 한 실험적 매거진 ... HTML과 PDF" --name future_relics
python3 -m gentle_monster magazine "<브리프>" --image photos/a.jpg --credit "Photo: 이름" --rights own   # 권리를 밝힌 사진은 실린다
python3 -m gentle_monster research          # research/*.md 를 원장에서 다시 만든다 + 범위(coverage) 출력
python3 tests/test_magazine.py              # 63개 검사, RED 9개 포함
```

결과는 `out/<이름>/magazine/` 에 쌓인다(git 밖):
`index.html` · `magazine.pdf` · `assets/*.svg` · `plan.json` · `hypotheses.json` · `assets.json` · `tokens.json` · `qa.json` · `QA_REPORT.md`.

## 규칙 — Gemini 를 쓰지 않는다

**사용자 지시(2026-10-09): "Gemini 쓰지 않는다".** 매거진 시스템(`gentle_monster/magazine/`)은 Gemini 도, 다른 언어
모델도 부르지 않는다. 키가 있어도 마찬가지다. `gentle_monster/llm.py` 를 import 하지 않으며, `tests/test_magazine.py` 가
패키지의 모든 파일에서 그 import 가 없는지와 빌드 중 `llm` 모듈이 로드되지 않는지를 확인한다. 글을 더 좋게 하려면
템플릿과 연구 원장을 고친다.

## 단계와 파일

| 단계 | 파일 | 하는 일 |
|---|---|---|
| 연구 원장 | `research/sources.json` · `magazine/catalogue.py` | 출처(종류 · **읽은 정도** fulltext/snippet) · 주장(주체 × 축, official_statement / reported_fact / interpretation). `validate()` 가 인용 없는 주장, 공식 출처 없는 '공식 입장', 조각만 보고 붙인 'high' 를 잡는다. `compare()` 는 행렬이지 순위가 아니다 |
| Drift | `magazine/drift.py` | SE_NEW DRIFT 규칙을 개념에 옮겼다 — [`research/drift/SE_NEW_DRIFT.md`](../research/drift/SE_NEW_DRIFT.md) |
| 방향 · 계획 | `magazine/planner.py` | 브리프(한/영) → 주제어 · 요청 출력. 주제에 가장 가까운 GM 연구 노드 4개에서 걸음 6번씩. 같은 읽기로 끝난 걸음은 다시 표류(최대 3번). 7개 기준으로 비교해 하나를 고르고, 진 방향과 이유도 지면에 싣는다 |
| 자산 | `magazine/assets.py` · `magazine/plates.py` | 메타데이터 15칸. `publishable()` = 권리 확보 ∧ 검증됨 ∧ 파일이 실제로 있음. 레퍼런스는 **출처로만**, 그림 자리는 '보류'. 생성 도판(SVG)은 "drawing, not a photograph" 라고 적힌다 |
| 디자인 시스템 | `magazine/design.py` | 토큰(종이·잉크·강조색은 고른 분야에서, 나머지는 섞어서), 1.25 비율 활자, 12단 · 5 mm 거터 · 14 pt 기준선, 230 × 300 mm. 화면 규칙과 인쇄 규칙을 따로 낸다 |
| 렌더 | `magazine/render.py` · `magazine/pdf.py` | 쪽 유형 12가지. 사실은 출처 번호 + 종류 + 읽은 정도와 함께, 실험은 EXPERIMENT 표시와 함께. PDF 는 Chromium 직접 호출 |
| QA | `magazine/qa.py` | 연구 · 창작 · 제작. PASS / WARNING / FAIL / NOT_CHECKED. **NOT_CHECKED 는 통과가 아니다** |

## 점수는 무엇을 재나 (전부 원장에서 계산하는 휴리스틱 — 취향 판정이 아니다)

| 기준 | 정의 |
|---|---|
| source_traceability | 원리 중 출처가 있는 몫 |
| conceptual_distance | 1 − (출발 노드와 끝 노드의 낱말 겹침). 보조 지표. 크다고 좋은 것이 아니다 |
| editorial_coherence | 장치 중 쪽 유형에 대응하는 몫 (쪽 유형이 하나뿐이면 반으로) |
| visual_originality | 이 방향의 장치 중 다른 방향이 안 쓰는 몫 |
| brand_relevance | 끝 노드에 살아남은 **반복되는** 브랜드 연구 어휘(GM 주장 둘 이상에 나오는 낱말) ÷ 4, 상한 1. 0.25 미만이면 제외 |
| feasibility | 장치 중 그릴 수 있는 도판이나 글 지면이 있는 몫 |
| rights_compliance | 도판이 인쇄 가능한 몫. 지금은 전부 생성 도판이라 1.0 — **실제 이미지를 쓰기 시작하면 이 값이 처음으로 의미를 갖는다** |

## QA 가 실제로 재는 것

브라우저가 재는 것은 브라우저로 잰다. 인쇄 크기(869 × 1134 px, `html.print-sim`)에서 넘침 · 그림 로드 · 격자선 정렬 ·
그림 비율(늘림 금지, 잘림은 풀블리드만) · 보이는 한글(CJK 글꼴이 없다). 375 px 에서 가로 스크롤과 **페이지에 가려
잘린 내용**. PDF 쪽수 = HTML 쪽수.

### 만들면서 잡은 거짓 신호

1. **375 px 가 실은 500 px 였다.** `chrome --headless=new --window-size=375,…` 는 뷰포트를 500 으로 올린다.
   첫 판은 "문서 폭 500 px → FAIL" 이라고 했다 — 거짓 빨강이다. 이제 뷰포트를 같이 받아, 요청한 폭이 아니면
   NOT_CHECKED 를 내고, 측정은 375 를 지키는 `headless_shell` 로 한다.
2. **그런데 375 에서 진짜 문제가 있었다.** 문서 폭은 360 이라 '가로 스크롤 없음' 이었지만, 이미지 카탈로그의
   항목이 451 px 까지 나가 `.page{overflow:hidden}` 에 **가려져 있었다.** 문서 폭만 보는 검사는 이것을 영영 못 본다.
   그래서 화면 밖으로 나간 요소를 따로 센다. 고친 것: 격자 칸에 `minmax(0,1fr)`.
3. **연구 원장의 'high' 19개.** 하위 조사가 조각만 보고 high 를 붙였다. `validate()` 가 잡았고 medium 으로 내렸다
   (`confidence_note` 에 이유).

## 완료 기준에 대해 — 된 것과 안 된 것

| # | 기준 | 상태 |
|---|---|---|
| 1 | 근거와 출처가 있는 브랜드 리서치 | 됨 — 93 출처 · 63 주장. **단 전부 검색 조각**(원문 접속이 막혔다) |
| 2 | 브랜드 · 매거진 비교 분석 | 됨 — `research/comparative_analysis/matrix.md`. 매거진의 활자 · 격자 · 시퀀스 축은 거의 비어 있다 |
| 3 | 검증 상태가 명시된 Drift 방법론 | 됨 — 원문 전문, 인용 15개 자동 재검 |
| 4 | 독창적인 편집 콘셉트 후보 | 됨 — 방향 4개, 비교표 |
| 5 | 선택된 방향과 쪽별 계획 | 됨 — `plan.json` |
| 6 | 실제 이미지와 출처 메타데이터 | **반쯤.** 메타데이터는 있다. 실제 이미지는 하나도 못 받았다(접속 차단) → 레퍼런스는 보류, 지면은 생성 도판 |
| 7 | 웹에서 열리는 매거진 | 됨 — 18쪽 |
| 8 | 실제 생성된 PDF | 됨 — 18쪽, 230 × 300 mm |
| 9 | QA 보고서 | 됨 — WARNING(FAIL 0): 원문 미열람 1, 외부 링크 NOT_CHECKED 2 |
| 10 | 확인 못 한 것과 남은 일 | 아래 + 지면의 Critical Review |

## 남은 일

- **원문 열람.** 외부 접속이 되는 환경에서 `sources.json` 의 URL 을 열어 `verification: fulltext` 로 올리기. 지금은 0/63.
- **실제 이미지.** 권리가 확인된 이미지(브랜드 프레스 키트의 사용 조건 등)를 `--image … --rights licensed` 로. 권리 확인은 사람이 한다.
- **지면 글.** 지금 글은 원장에서 조립한다(템플릿 + 인용). 문장 품질은 템플릿과 연구 원장(인용의 질 · 원문 열람)을
  손봐서 올린다 — 모델 단계는 두지 않는다(아래 규칙).
- **매거진 편집 축 조사.** 활자 · 격자 · 이미지 시퀀스 · 인쇄 사양은 거의 조사하지 못했다(원장 `not_checked` 10번).
- **한글 지면.** CJK 글꼴이 설치된 곳에서는 한글 본문이 가능하다. 지금은 QA 가 보이는 한글을 경고한다.
- 디스코드 `!젠몬` 자연어 경로에는 아직 안 붙였다.
- **이 심판이 못 잡는 것:** 글이 좋은가, 바깥 분야의 연결이 설득력 있는가, 원장에 '전문' 이라고 거짓으로 적는 것.
