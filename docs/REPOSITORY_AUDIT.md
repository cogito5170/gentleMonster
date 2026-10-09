# 저장소 조사 (Phase 0) — 2026-10-09

코드를 고치기 전에 본 것. 매거진 시스템을 어디에 붙일지와 무엇을 다시 쓸지를 여기서 정했다.

## 무엇이 있었나

| 자리 | 하는 일 | 매거진 시스템에서 |
|---|---|---|
| `gentle_monster/` (공간 디자인 파이프라인) | 브리프 → 시놉시스(Gemini) → 레이아웃 PDF · 무드보드 PDF(A3 펼침 8장) · 청사진 · MP4 · 웹 페이지 | **같은 패키지 안에** `gentle_monster/magazine/` 로 붙였다. 경로(`paths.job_dir`, `paths.chromium`)와 출력 규약(`out/<작업>/`, git 밖)을 그대로 쓴다 |
| `gentle_monster/moodboard.py` | 잡지 문법(cover · contents · manifesto · pair · bleed · board · collage · sequence), 사진 측정, "generated" 라벨 | 펼침 문법과 "생성물은 생성물이라고 적는다" 원칙을 이어받았다. 코드는 직접 재사용하지 않았다 — 무드보드는 job.json(공간)이 입력이고 매거진은 연구 원장이 입력이다 |
| `gentle_monster/engine/` | 토큰 → 페이지 → 브라우저 심판(V·J) → se_new 정책 | "심판은 모델이 아니라 Chromium" 원칙을 그대로 따랐다(`magazine/qa.py`). RED 테스트 방식도 같다 |
| `gentle_monster/photos.py` | 사진/레퍼런스 판별, 양식 측정 | 이번 수직 기능에서는 안 썼다(실제 사진이 없다 — 아래) |
| `docs/portfolio/` | 지원자 포트폴리오 원고(철학: 멈춘다 · 머문다 · 다시 온다) | 매거진의 내용으로 쓰지 않았다. 개인 원고이고, 브랜드 연구가 아니다 |
| `tests/` | 자체 `ok()` 러너, 브라우저 없으면 '건너뜀' | `tests/test_magazine.py` 를 같은 양식으로 썼다 |

**"기존 HTML 잡지 카탈로그"** 는 이 저장소에 없었다. 가장 가까운 것은 se_new 의 `visual_culture_platform`(`magref`) —
잡지 표지·펼침 레퍼런스를 출처·권리와 함께 모으는 도구다. 그쪽 README 스스로 "실제 웹사이트에는 한 번도 접속하지
않았다(외부 접속이 막혀 있었다)" 고 적는다. 이미지·캡션·태그·링크가 담긴 카탈로그 파일은 두 저장소 어디에도 없었다.
그래서 **분석할 기존 이미지가 없다** — 없다는 것을 여기 적는다.

## SE_NEW Drift — 원문은 se_new 저장소 안에 있다

브리프가 열어 둔 물음("SE_NEW 의 Drift 가 무엇인가, 네덜란드 DRIFT 인가")의 답은 조사로 나왔다.
**SE_NEW 의 Drift 는 se_new 저장소가 스스로 정의한 방법론이다.** 네덜란드 스튜디오 DRIFT 와는 관계없다.

- 원문: `novel/DRIFT.md`, `novel/shock.py`, `novel/diffusion.py`, `mathdrift/README.md`, `mathdrift/measure.py`, `mathdrift/ops.py`
- 커밋 `79dab33` (2026-09-30), 인용 15개를 `research/drift/se_new_drift.json` 에 적었고 QA 가 se_new 체크아웃에서 **글자 그대로** 다시 찾는다
- 요약과 이 프로젝트의 해석(원문에 없는 것)의 구분: [`research/drift/SE_NEW_DRIFT.md`](../research/drift/SE_NEW_DRIFT.md)

## 환경 제약 (실측)

| 무엇 | 결과 |
|---|---|
| `curl https://www.gentlemonster.com/` | 프록시가 CONNECT 에 **403** (정책 거부). 032c · wikipedia 도 같다 |
| WebFetch (gentlemonster.com, wikipedia, domusweb) | `getaddrinfo ENOTFOUND` — 전부 실패 |
| WebSearch | **됨.** 연구 원장 93개 출처 · 63개 주장은 전부 이것으로 모았다 → 전부 `read: snippet` |
| PyPI (`pip install playwright`) | 이름 해석 실패 → Python Playwright 없음. 기존 테스트의 브라우저 부분은 '건너뜀' 으로 돈다 |
| Chromium | `/opt/pw-browsers` 에 있다. 매거진은 Playwright 없이 Chromium 을 **직접** 부른다(PDF 출력, DOM 측정) |
| `chrome --headless=new --window-size=375,…` | 창이 **500 px 아래로 안 줄어든다**(실측: 뷰포트 500). 그래서 375 px 측정은 `headless_shell` 로 한다(실측: 375) |
| 글꼴 | Liberation · DejaVu, 그리고 **한글을 덮는 WenQuanYi Zen Hei** (`fc-list :lang=ko`). 첫 조사에서는 이름을 `cjk\|noto\|nanum` 으로 grep 해서 **"한글 글꼴이 없다" 고 잘못 적었다** — 그 판단으로 첫 판 지면을 영문으로 냈다. 지금 지면은 한국어이고, QA 는 이름이 아니라 fontconfig 에 언어로 묻는다 |

## 결정

1. 별도 서버·에이전트를 만들지 않았다. 모듈 하나(`gentle_monster/magazine/`)에 단계를 나눴다.
2. 모델 호출 없이 돈다. 연구는 원장 파일, 변형은 결정적 Drift, 글은 원장에서 조립한다.
3. 실제 이미지를 받을 수 없으므로(위 표), 레퍼런스는 **출처로만** 싣고 그림 자리는 '보류' 로 비워 둔다.
   사용자가 권리를 밝힌 사진(`--image … --rights own`)은 실린다.
