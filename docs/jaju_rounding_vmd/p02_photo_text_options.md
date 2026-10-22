# 2쪽 — 사진 위에 메시지, 세 안

작성일: 2026-10-22. PDF: `layout/p02_photo_text_options.pdf` (3쪽) · `python3 tools/jaju_layout/p02_photo_text_options.py`.
사용자: "해당 이미지 위에 해당 문구를 기입하라. 포트폴리오 사례를 참고하여 3가지의 안을 제시하라."
사진: `assets/cover/opening_book_dark.jpg` (사용자가 준 어둡게 한 흑백판, 1736×1138). 쪽 전체에 깔고 좌우가 약 12mm씩 잘린다.
글: 제목 '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.' + 프롤로그 일곱 문장. 사진의 밝기가 어디서나 중간 회색(80–140)이라
흰 글자는 사진을 어둡게 덮은 자리에만, 어두운 글자는 밝은 빈 면에만 놓았다.

| 안 | 사례 | 배치 | 글자 | 최종 글꼴 |
|---|---|---|---|---|
| 1안 | Galatasaray S.K. — 사진이 아래에서 검정으로 녹고 그 위에 글 | 쪽 아래 40% 를 검정으로 녹이고, 왼쪽 62mm(1/5)에서 시작 | 굵은 고딕 19pt 한 줄 + 회색 10pt 한 문단, 마지막 문장만 흰색 | Pretendard Bold · Regular |
| 2안 | ETÉREO — 책의 면에 인쇄된 세리프 제목 + 작은 본문 | 사진 속 책의 빈 면에, 면의 기울기(−6.8°)대로 돌려 '인쇄' (곱하기 합성) | 13pt 두 줄 제목 + 6.6pt 일곱 줄, 어두운 잉크 | 명조 Noto Serif KR Regular · Light |
| 3안 | Desjobert — 사진 위 반투명 글 상자 | 오른쪽 면 위 82×164mm 검정 72% 상자, 인물 · 마네킹은 가리지 않음 | PROLOGUE 표지 글 + 13pt 두 줄 제목 + 7.8pt 문장(한 문장 한 줄) + 영어 이탤릭 | Pretendard SemiBold · Regular, Lora Italic, IBM Plex Mono |

- 시안의 한글은 모두 문천역정흑(이 환경의 유일한 한글 글꼴). 쪽 오른쪽 위 '안' 표시는 비교용.
- 2안은 사진 속 책이 이 포트폴리오 자신이라는 장치 — 책을 펼치면 첫 문장이 이미 그 면에 인쇄되어 있다.

## 1안 · 3안 InDesign (2026-10-22)

사용자: "1안 3안을 인디자인 파일로 보내라."
- `indesign/p02_photo_galatasaray/` · `indesign/p02_photo_desjobert/` (+ 각 `.zip`): `.idml` · `.jsx` · 기준 `.pdf` · `Links/opening_book_dark.jpg` (3안은 `Document Fonts/` Lora Italic · IBM Plex Mono + OFL).
- 사진 틀은 재단 여유 3mm 까지. 1안 검정 녹임 = 검정 사각형 + 그레이디언트 페더(위 30% 0% → 58% 75% → 72% 96%),
  3안 글 상자 = 검정 72% 불투명도 + 0.15mm 회색 선. 1안 본문 끝 문장만 흰색. 쪽 번호 2.
- 그레이디언트 페더 · 불투명도는 IDML 에 처음 넣는 효과라 InDesign 에서 확인이 필요하다. IDML 이 열리지 않거나 페더가 빠지면 같은 폴더의 `.jsx` 로 짓는다.
- 만드는 법 `python3 tools/jaju_layout/indd_p02_photo.py` (빌더 indd_p03.py 에 사진 · 불투명도 · 페더 · 선을 더했다).

## 리포타주 판 (2026-10-22)

사용자가 준 사례('Behind the Scenes, Beyond the Ordinary': 어두운 인물 사진 왼쪽 2/3 + 오른쪽 글 단)를 따라 다시 짰다.
`layout/p02_reportage.pdf` · `python3 tools/jaju_layout/p02_reportage.py`.
- 사진을 왼쪽으로 밀어(x −64mm) 마네킹 · 인물이 왼쪽 2/3, 오른쪽 밝은 책장은 검정(#0D0E10)으로 녹여 글 단(x 170mm). 사진 쪽도 22–60% 어둡게.
- 글 단: 표지 글 `PROLOGUE / FROM THE INSIDE`(고정폭 회색) → 크림색 제목 두 줄 19pt → 부제 `A VMD WHO LOOKS OUT FROM THE INSIDE`(고정폭 크림)
  → 한국어 두 문단(보는 자리 / 멈추고 웃는 사람, 마지막 문장만 크림) → 영어 대문자 한 문단(사례의 대문자 본문). 양 가장자리에 필름 같은 옅은 숫자.
- 최종 글꼴: 제목 Noto Serif KR Light(사례의 가는 세리프), 본문 Pretendard, 표지 글 · 부제 IBM Plex Mono, 영어 Instrument Sans.
- InDesign (2026-10-22, 사용자 "인디자인 파일로 제공하라"): `indesign/p02_reportage/` (+ `.zip`) — `.idml` · `.jsx` · 기준 `.pdf` · `Links/` ·
  `Document Fonts/`(IBM Plex Mono · Instrument Sans + OFL). 문단 스타일 6개(Label · Title · Sub · Body · English · Edge), 어둡게 하기는 검정 사각형 두 개의
  그레이디언트 페더(위→아래 · 왼쪽→오른쪽), 가장자리 숫자는 90° 돌린 글 틀. 사진은 재단 여유까지 덮도록 약 3% 키움.
  만드는 법 `python3 tools/jaju_layout/indd_p02_rep.py`. InDesign 으로 열어 보지 못했다.
