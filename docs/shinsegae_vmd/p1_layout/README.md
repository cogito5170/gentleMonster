# P1 지면 파일

**표지 + 1쪽은 B안(Galatasaray 방식)으로 정했다** (사용자 결정, 2026-10-21). `cover_b.*` 가 현재본이고, `cover_p1.*` 는 이전 시안이다.

| 파일 | 내용 | 만드는 법 |
|---|---|---|
| `cover_p1.pdf` | 표지 + 1쪽(PROLOGUE · 이야기 단락) 시안 | `python3 tools/p1_layout/cover_p1.py` |
| `cover_p1.idml` | 같은 두 쪽의 InDesign 문서 | 〃 |
| `cover_p1.jsx` | 같은 두 쪽을 InDesign 안에서 짓는 스크립트 (IDML 이 안 열릴 때) | 〃 |
| `Links/cover.jpg` | 표지 이미지 (사용자 제공, 1296 × 912 px) | — |
| `cover_b.idml` · `cover_b.jsx` | **B안 표지 + 1쪽 InDesign 문서 · 스크립트** (`cover_b_indesign.zip` = 둘 + Links) | `python3 tools/p1_layout/cover_b.py` |
| `cover_options.pdf` | 표지 + 1쪽 재수정 두 안 (A · ETÉREO / B · Galatasaray) | `python3 tools/p1_layout/cover_options.py` |
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

## B안 InDesign 파일 (cover_b)

- `cover_b_indesign.zip` 을 풀면 `cover_b/` 폴더에 IDML · JSX · `Links/cover.jpg` 가 함께 있다. 이 구조를 지켜야 그림이 연결된다.
- **JSX 를 먼저 권한다.** InDesign 안에서 지으므로 1쪽 대표 이미지의 페이드(그레이디언트 페더)까지 그대로 들어간다.
- **IDML 에는 페이드가 없다.** 열린 뒤 1쪽 오른쪽 사진 틀을 골라 `효과 > 그레이디언트 페더`: 유형 선형 · 각도 180° · 불투명도 정지점 100% 를 위치 62% 로, 0% 를 위치 100% 로.
- 색상 견본: Night(11 11 11) · White · Gray Light(204) · Gray Mid(138). 문단 스타일 12개(Tiny · Title · Message KO/EN · Name · Role · Head · Body KO/EN …), 글꼴은 Pretendard 하나.
- IDML · JSX 모두 이 환경에 InDesign 이 없어 열어 보지 못했다. XML 형식과 스크립트 문법만 검사했다.
