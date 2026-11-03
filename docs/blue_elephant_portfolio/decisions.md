# 블루엘리펀트 Creative Intern 포트폴리오 — 결정 기록

바탕: 0_기업 분석 세션이 보낸 자료(cogito5170/gentleMonster @ claude/gracious-edison-inoq0z — docs/company_analysis/blue_elephant/02b_captures.md · 04_analysis.md · 05_user.md).
JAJU 포트폴리오와는 별개 작업.

| 날짜 | 결정 |
|---|---|
| 2026-10-30 | 지원서 '업무 유관 URL'(선택)은 **우선 생략**한다 (사용자: "우선 URL은 생략한다."). 개인 인스타그램(ju_03.25) · 사진 모음 링크는 넣지 않는다 — 사진은 필요하면 포트폴리오 PDF 안에서만 보여 준다. |

## 프로젝트 묶음 제목 후보 (2026-11-02, 미정)
사용자: "해당 프로젝트(1 웹디자인 · 2 전광판 · 3 전시 실외 · 4 전시 실내 · 5 SNS 운영)를 담을 수 있는 영어 단어의 제목 … '다중의 작업이 가능한'을 내포할 수 있는 단어를 추천하라."
- 공통점: 다섯 작업 모두 같은 사진들을 서로 다른 '틀'(웹 화면 · 전광판 · 실외 진열창 · 실내 액자 · 인스타그램 카드)에 넣는다. 블루엘리펀트 = 안경 프레임.
- 권함: **MULTIFRAME** (여러 틀 — 다중 + 프레임). 다른 후보: RANGE · FACETS · PRISM · ACROSS · VERSATILE.
- 11-02 추가 — 사용자: "VERSATILE과 같은 유의어를 더 추천해라. 강하고 직관적인 단어를 원한다."
  권함 **ADAPT**(매체에 맞춰 바꾼다 — 짧은 동사) · **ALL-ROUND**(만능). 그 밖에 FLEX('플렉스' 과시 뜻 주의) · SHIFT · AGILE · OMNI · MULTIPLY · CHAMELEON · PROTEAN(강하지만 덜 직관적).

## 표지 PROTEAN — 버튼 글 · 디자인 요소 (2026-11-02)
사용자: "포트폴리오 커버를 제작 중이다. 제목은 PROTEAN 으로 설정했다. 우측 하단 버튼에 사용자를 설명할 수 있는 영단어를 넣어라. 또한, 현재의 틀을 바탕으로 '디자인적' 요소를 추가할 수 있다면 추가한 안도 제안해라."
→ `cover/cover_mock.pdf` (A 버튼 글 · B 디자인 요소) · `python3 tools/blue_elephant/cover_mock.py` · 바탕은 사용자 화면 `cover/cover_in_progress.jpg`
- 버튼 글 권함: **SPACE · LENS · STYLE** (건축 · 사진과 안경 렌즈 · 패션 — 공고 우대 '패션 · 사진 · 건축', 인스타그램 소개 'DESIGNER'). 가운데 '2026' 은 오른쪽 위와 겹쳐 글로 바꿈.
  다른 세트: ARCHITECTURE · PHOTOGRAPHY · FASHION (공고 낱말 그대로, 길다) / OBSERVE · FRAME · STYLE (하는 일, 동사) / DESIGNER · 2026 · PORTFOLIO (지금 틀 유지).
- B 디자인 요소: 사전 뜻풀이 한 줄(pro·te·an … able to take many forms) · 제목 O 를 렌즈처럼 감싼 가는 원 · 버튼 번호 01–03 · 맨 위 눈금 기준선 · 네 모서리 뷰파인더 · 오른쪽 렌즈 초점 괄호 'LENS — 02' · 세로 'FAMILIAR UNFAMILIAR' · 'No. 00 / COVER'.
- 제목 철자: 메시지의 'PROTEN' 이 아니라 화면대로 **PROTEAN** 이 맞다.

## 표지 문구 '나는 ~가 가능합니다' 세 안 (2026-11-02, 미정)
사용자: 공고(담당업무 · 자격요건 · 우대사항)를 참고해 2–3줄 영어로 '나는 ~가 가능합니다!'를 전하는 세 안. 참고 꼴: "Shaping what's next. / Through bold digital identity."
- A (권함) One eye, many forms. / From thumbnail to campaign, / I shape what every frame needs.
- B Space trained my eye. The lens sharpened it. / Now it's ready for every screen — / detail page, banner, feed.
- C Imagine it. Frame it. Deliver it. / Retouching, layout, AI-made visuals — / every file in place, every deadline met.
- 쓰지 않은 것: Premiere · After Effects · Figma(사용자 답 UQ2 — 써 본 적 없음), 영상 편집. AI 는 사용자 결정(적극 활용)대로 넣음.

## SNS 쪽 — 겹친 아이폰 셋 (2026-11-03)
사용자: 인스타그램 카드 셋 쪽을 TV Azteca 인스타그램 목업 꼴로 — 맨 위 로고 비움 · 아이폰 셋 안에 각 페이지 · 사례처럼 겹침 · 검은 바탕.
→ `sns_phones/sns_phones.png`(3840 × 2160) · `sns_phones.pdf`(1920 × 1080) · `python3 tools/blue_elephant/sns_phones.py`
- 가운데 휴대폰(격자 9장)이 앞에 크게, 양옆(바위 · 미술관)은 뒤에서 조금 위로. 화면 안은 인스타그램 화면(맨 위 줄 · 스토리 · 게시물 머리 · 사진 · 반응 · 아래 메뉴).
- 맨 위 가운데(y 약 40–190px)는 로고 자리로 비워 둠. 좋아요 수 · 댓글 같은 지어낸 숫자와 글은 넣지 않음.
- 사진은 사용자 카드 화면에서 잘라 냄(post_left · post_grid · post_right, 해상도 낮음) — 원본으로 바꾸면 더 선명.
- 11-03: 사용자 "스크린의 좌측 상단 Jeonghyeokju 부터 우측 하단 저장 표시까지 화면을 흰색으로 변환하라. 3개 모두. 1920x1080(픽셀) 일러스트 파일로."
  → `sns_phones/sns_phones_blank.svg`(일러스트레이터에서 열면 층별 벡터, 1920 × 1080 px) · `.pdf`(1920 × 1080 pt = 일러스트레이터 1920 × 1080 px, 글꼴 포함) · `.png` 미리 보기.
  게시물 칸(아이디 줄 ~ 반응 · 저장 줄)을 흰 사각형 POST_AREA_LEFT · RIGHT · CENTER 로 — 쪽을 얹거나 클리핑 마스크로. 로고 자리 LOGO_AREA(빈 틀). `python3 tools/blue_elephant/sns_phones_blank.py`
