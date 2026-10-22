# 2쪽 메시지 쪽 — 세 안 (검정 바탕 + 글)

작성일: 2026-10-22. PDF: `layout/p02_message_options.pdf` (4쪽: 표지 → 1안 → 2안 → 3안) · `python3 tools/jaju_layout/p02_message_options.py`.
사용자: 사례 1(Galatasaray S.K.) · 2(NEA Magazine)처럼 첫 쪽은 사진으로 인상, 둘째 쪽은 검정 바탕에 글로 메시지.
조건: 검정 바탕 · '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.' · 프롤로그 일곱 문장(한국어 필수, 영어 선택) · 문단 바꿈 허용.
(사용자가 붙인 원문에는 문장이 두 번씩 겹쳐 붙어 있어, 겹친 것을 걷어 낸 일곱 문장 — 프롤로그와 같은 글 — 을 썼다.)

## 사례에서 읽은 것

| | Galatasaray S.K. | NEA Magazine |
|---|---|---|
| 정렬 | 왼쪽, 쪽 폭의 약 1/5 에서 시작 | 가운데 |
| 제목 | 굵은 산세리프 한 줄, 흰색 | 가는 세리프 대문자, 밝은 회색 |
| 본문 | 회색 한 문단, 3줄 | 두 언어를 각각 한 덩어리로, 사이를 넓게 |
| 여백 | 글 아래가 모두 검정 | 위 · 아래 고르게 |

## 세 안

| 안 | 배치 | 글 | 글꼴(최종) |
|---|---|---|---|
| 1안 · Galatasaray | 왼쪽 62mm 에서 시작, 위 1/3 에 모음, 아래는 비움 | 굵은 제목 한 줄 + 일곱 문장을 한 문단(회색), 마지막 문장만 흰색 | Pretendard Bold / Regular |
| 2안 · NEA | 가운데 정렬 | 제목 + 영문 대문자 부제 → 한국어 세 덩어리(보다 · 지나가다 · 되려 한다) → 영어 한 덩어리 | 국문 명조(KoPub바탕 Light · Noto Serif KR Light) · Instrument Sans |
| 3안 · 유리 | 가운데 세로선 = 유리. 왼쪽(밖) · 오른쪽(안) | 제목 앞 절반 '밖에서 보면 상품이 보이고,'를 거울 글자(어두운 회색), 뒤 절반 '안에서 보면 사람이 보인다.'를 흰색으로. 아래 두 단: 밖의 세 문장 / 안의 네 문장 + 영어 | Pretendard SemiBold · Regular · Lora Italic · IBM Plex Mono |

- 3안의 거울 글자는 표지 사진의 거꾸로 읽히는 유리 글자(SHOE SHOP)를 받는다 — 프롤로그 "안에서 보면 가게 이름은 거꾸로 읽히고".
- 시안의 한글은 모두 문천역정흑(이 환경의 유일한 한글 글꼴)이다. 안마다의 글꼴 차이는 InDesign 단계에서 위 글꼴로.
- 쪽 오른쪽 위의 작은 '1안 · …' 표시는 비교용 — 최종본에서 지운다.

## 확인할 것

- 이 쪽이 들어가면 3쪽 Prologue 와 글이 같아진다. Prologue 를 뺄지, 다른 글로 바꿀지 정해야 한다.
- 지금 2쪽의 책 사진(opening_book.jpg)을 이 쪽으로 바꾸는지, 그 뒤로 미는지.

## 2안 InDesign (2026-10-22)

사용자: "2안을 인디자인 파일로 제공하라."
- `indesign/p02_message_nea/` (+ `.zip`): `.idml` · `.jsx` · 기준 `.pdf`('안' 표시 뺌) · `Document Fonts/`(Crimson Pro · Instrument Sans + OFL).
- 문단 스타일 6개: Title(명조 17pt, 자간 20) · Subtitle(Crimson Pro 9pt, 자간 140) · Body KO(명조 Light 9.6/17) · Body KO Next(덩어리 사이 8pt) ·
  Body KO Last(흰색) · Body EN(Instrument Sans 8/13). 모두 가운데 정렬. 쪽 번호 2.
- 국문 명조는 Noto Serif KR(Light · Regular)로 지정 — 따로 설치. KoPub바탕을 쓰려면 문단 스타일 세 개의 글꼴만 바꾸면 된다.
- 만드는 법 `python3 tools/jaju_layout/indd_p02.py` (빌더는 indd_p03.py). InDesign 으로 열어 보지는 못했다.
