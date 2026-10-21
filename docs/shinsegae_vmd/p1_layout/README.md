# P1 지면 파일

| 파일 | 내용 | 만드는 법 |
|---|---|---|
| `cover_p1.pdf` | 표지 + 1쪽(PROLOGUE · 이야기 단락) 시안 | `python3 tools/p1_layout/cover_p1.py` |
| `cover_p1.idml` | 같은 두 쪽의 InDesign 문서 | 〃 |
| `cover_p1.jsx` | 같은 두 쪽을 InDesign 안에서 짓는 스크립트 (IDML 이 안 열릴 때) | 〃 |
| `Links/cover.jpg` | 표지 이미지 (사용자 제공, 1296 × 912 px) | — |
| `page09_layout.pdf` | 9쪽 '하나의 창 (제안)' 시안 + 명세 | `node tools/p1_layout/page09.mjs` |

## InDesign 에서 여는 법

1. **IDML:** 이 폴더째 내려받아 InDesign 에서 `파일 > 열기 > cover_p1.idml`. 열리면 `파일 > 저장`으로 `.indd` 가 된다.
   그림이 '연결 없음'으로 뜨면 연결 패널에서 `Links/cover.jpg` 로 다시 연결한다.
2. **JSX (IDML 이 열리지 않을 때):** `cover_p1.jsx` 와 `Links/` 를 같은 폴더에 두고, InDesign 의 스크립트 패널(창 > 유틸리티 > 스크립트)에서
   사용자 폴더에 넣어 두 번 클릭한다. 새 문서에 같은 두 쪽이 지어진다.

## 서체

| 자리 | InDesign 문서 | PDF 시안 (이 환경에 있는 글꼴) |
|---|---|---|
| 제목 · 쪽 번호 (세리프) | EB Garamond | Crimson Pro |
| 머리말 · 한글 본문 · 영문 캡션 (산세리프) | Pretendard | Instrument Sans + 문천역정흑(한글) |

두 글꼴이 없으면 InDesign 이 '글꼴 없음'으로 표시한다. `문자 > 글꼴 찾기`에서 가진 글꼴로 바꾸면 문단 스타일 전체에 반영된다.
문단 스타일: Header · Header Bold · Cover Title · Cover Name · Lead KO · Caption EN · Title · Folio.

## 확인할 것

- 표지 이미지가 1296 × 912 px 이다. A4(297mm) 폭에 인쇄하면 약 110 ppi — 화면용으로는 충분하지만 인쇄하려면 가로 3500 px 이상의 원본이 필요하다.
- 1쪽 오른쪽 사진은 표지 이미지의 왼쪽(마네킹의 등)을 잘라 다시 쓴 자리다. 직접 찍은 사진으로 바꿔도 된다.
