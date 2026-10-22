# B13 — B12 + 03 쪽을 2-2 세션 확정 스토리로, 04 의 겹치는 사진 정리

작성일: 2026-10-21. PDF: `layout/plan_b13.pdf` (17쪽 · 약 7.3MB) · `python3 tools/jaju_layout/plan_b13.py`.
사용자: "2-2 의 변경된 스토리를 반영하여 수정하라."
근거: 2-2 세션(claude/awesome-keller-otac19 09f64c3) `p03_thoughts_options.md` 3안 확정 · `p03_story_options.md` 안 A.

## 03 Where people stop.

- 본문: 멈춘 사람은 대개 짧은 질문 하나를 하고 있다. 조금 더 있을까? 뭐 먹지? 어느 게 맛있어 보이지? (+ 영문)
- 맺음(왼쪽 아래): 나도 가게 앞에서 질문 하나를 한다. 어떻게 놓으면 지나가던 사람이 걸음을 멈출까. (+ 영문)
- 사진: 2열 × 3줄(89.5 × 46.5mm), 사람마다 점선 틀(좌표는 2-2 의 p03_options.py), 바다 → 거리 → 가게.

| N° | 사진 | 자리 | 질문 (짐작) |
|---|---|---|---|
| 01 | PH-01 | 얕은 물 | 조금 더 있을까? |
| 02 | PH-17 | 파라솔 옆 | 어디가 제일 잘 보이지? |
| 03 | PH-11 | 가게 계단 | 잠깐 앉을까? |
| 04 | PH-07 | 불판 앞 | 다 익었나? |
| 05 | PH-04 | 간판 앞 | 뭐 먹지? |
| 06 | PH-06 | 메뉴판 앞 | 어느 게 맛있어 보이지? |

- 캡션 = N° · 자리 · 질문 · 잰 HEX. 시간대 글자 없음. 데이터 줄 `17 FRAMES / 06 SHOWN · SIX PLACES, SIX QUESTIONS — MY GUESS`.
- B12 의 9장 그리드는 2-2 확정안(6장)으로 바뀌었다. 빠진 사진: PH-09 · PH-16 · PH-12 · PH-03.

## 04 What made me stop.

- d) Through the rail(PH-07)이 03 의 N°04 와 겹쳐 → **d) Sprout(PH-10) — 마른 잎 사이, 초록 싹 하나**. PH-10 은 책에서 처음 쓰는 사진.
- b) Pink(PH-01 을 크게 잘라 낸 한 사람)는 03 N°01 과 같은 사진이지만 '넓게 → 한 점'이라 그대로 둔다.

나머지 쪽은 B12(= B10) 그대로.

## B14 (2026-10-21) — 현재본

사용자: "맨 처음 커버 페이지를 해당 이미지로 대체한다. 이미지 다른 것은 추가하지 않는다."
- 표지 = 사용자가 준 흑백 사진(`assets/cover/cover_bw.jpg`) 한 장만 쪽 전체에. 글 · 바탕 띠 없음(사용자: "첫 커버 페이지는 이미지만 존재한다").
- 14 Often 의 N°01 과 뒤표지는 기존 컬러 표지 사진 그대로(지시가 '맨 처음 커버 페이지'만).
- `layout/plan_b14.pdf` (17쪽 · 약 7.6MB) · `python3 tools/jaju_layout/plan_b14.py`.

## B15 (2026-10-21) — 현재본

사용자: "4페이지의 좌측 레이아웃을 해당 이미지와 같이 수정한다." (2-2 세션 안 A 시안 캡처)
- 03 왼쪽 단을 시안의 배치로: 제목 한 줄 19pt `Where people stop.`(y 22) → 국문 본문(y 36) → 영문 이탤릭(y 70) → 맺음 국문(y 102) · 영문(y 118) → 고정폭 글 덩어리(y 148).
- 글은 확정 문구 그대로. 고정폭 덩어리: `17 FRAMES / 06 SHOWN` · `SEA → STREET → SHOP` · `SIX PLACES, SIX QUESTIONS — MY GUESS.`
- 오른쪽 사진 · 캡션과 다른 쪽은 B14 그대로. `layout/plan_b15.pdf` (17쪽 · 약 7.6MB) · `python3 tools/jaju_layout/plan_b15.py`.

## B16 (2026-10-21) — 현재본 (18쪽)

사용자: "2페이지를 새로 추가한 후 해당 이미지를 첨부하라. 이미지만 존재한다."
- 표지 다음(PDF 2쪽)에 사진 한 장만 있는 쪽: `assets/cover/opening_book.jpg`(1456×816, 표지 사진이 실린 책을 펼쳐 든 장면). 글 · 바탕 · 쪽 번호 없음.
- 사진이 쪽보다 넓어(1.78 : 1.41) 좌우가 조금 잘린다(왼쪽 손 · 오른쪽 글 단 가장자리).
- 본문 쪽 번호는 그대로(Prologue = 01) — 사진만 있는 두 쪽은 번호를 세지 않는다.
- `layout/plan_b16.pdf` (18쪽 · 약 7.8MB) · `python3 tools/jaju_layout/plan_b16.py`.

## B17 + 3쪽 InDesign (2026-10-22) — 현재본 (18쪽)

사용자: "커버를 포함해서 페이지 수를 카운트한다. 3페이지를 인디자인 파일로 제공하라."
- 쪽 번호 = 표지부터: 표지 1 · 책 사진 2 · Prologue 3 … 뒤표지 18. B17 은 바닥 줄 번호(01–15 → 03–17)와 쪽 참조
  (프롤로그 p.04 · p.08 · p.11, Proposal ← 07 · 10 · 14)만 바꾼 판. `layout/plan_b17.pdf` · `python3 tools/jaju_layout/plan_b17.py`.
- 3쪽(Prologue) InDesign: `indesign/p03_prologue/` (+ `indesign/p03_prologue.zip`) — `.idml`(열어서 .indd 로 저장) · `.jsx`(IDML 이 안 열릴 때
  스크립트로 같은 쪽) · `.pdf`(기준 시안) · `Document Fonts/`(Young Serif · Lora · IBM Plex Mono + OFL). 만드는 법 `python3 tools/jaju_layout/indd_p03.py`.
  - 한글은 Pretendard(Regular · Bold) — 이 환경에 없어 따로 설치해야 한다. 반투명 선 · 유령 글자는 바탕에 섞은 단색 스와치(Ghost · Rule · Cross).
  - InDesign 이 이 환경에 없어 열어 보지 못했다(XML 구조만 검사).
