# v2 16–19쪽 — PICTURE 마지막 두 펼침 (IDML 반영)

지원자가 보낸 `포트폴리오 16-19.idml` 에 원고를 넣고, 비어 있던 자리를 채웠다.

- 결과: [idml/포트폴리오 16-19 수정.idml](idml/) — InDesign 에서 열고 .indd 로 저장한다.
- 만든 스크립트: [scripts/idml_picture_16-19.py](scripts/idml_picture_16-19.py) — `python3 docs/portfolio/scripts/idml_picture_16-19.py 원본.idml 결과.idml`
- 이 두 펼침과 그 스토리만 고쳤다. 표지 펼침 · 마스터 · 다른 파일은 원본 그대로다.

## 이 IDML 에 든 것

IDML 안에서는 쪽 이름이 2–5 로 나온다(16–19쪽만 내보내서). 내용으로 보면 v2 지면 기록의 **G(Q2)** 와 **I(다리 ②)** 다.

| 쪽 | 펼침 | 사진 (대체 텍스트 · 촬영 정보) | 템플릿 상태 |
|---|---|---|---|
| 16–17 | Q2 · What makes a good picture? | 바다에 사람이 서 있는 사진, 접힘에 걸쳐 가운데 (23mm f/2 · 2026-09-11 17:37) | 본문 자리 둘(영어 자리 글) · © 2026 Template.Systems · Grid Exploration 003 · download now · Experimental Grid Exploration · Series · (003). 사진 캡션 없음 |
| 18–19 | 다리 ② PICTURE → ARCHITECTURE | 18: 그릴(어두운 배경, 연기 질감 · 23mm f/2 · 2026-09-09 17:22), 왼쪽 재단선까지 · 19: 그림 앞에 사람들이 모인 미술관 실내(2022-06-04 15:53), 오른쪽 재단선까지 | Grid Exploration 001 · 좁은 본문 자리 · 큰 글자 자리(오른쪽 재단선 밖 915pt 까지 넘침) · 라벨 둘 |

> v2 지면 기록에서는 G = 14–15, H(사진만) = 16–17, I = 18–19 였다. 이 파일에서는 Q2 펼침이 16–17 이다 — H 가 빠졌거나 자리가 바뀌었다. 전체 수정 때 쪽 순서를 다시 맞춘다.

## 16–17 · Q2

| 자리 | 전 | 후 |
|---|---|---|
| 16 왼쪽 위 | © 2026 Template.Systems | **PICTURE** (머리말) |
| 17 오른쪽 위 | Grid Exploration 003 | **MOMENT** (머리말 — v1 의 PICTURE / MOMENT 짝, STYLE 의 STYLE / MOOD 와 같은 규칙) |
| 16 본문 | A grid system is … | 아래 Q2 |
| 17 본문 | A grid system is … | 아래 Q2 마무리 + 영어 한 줄 (**새로 씀**) |
| 바다 사진 캡션 | 없음 | **Sea / (September, 5:37 pm)** — 16쪽 아래의 download now 상자를 사진 아래(8pt)로 옮겨 썼다 |
| 16 아래 (003) | (003) | 지움 — (003) 은 ARCHITECTURE 번호다 |
| 17 아래 | Experimental Grid Exploration · Series | 지움 |

**16쪽**

> **What makes a good picture?**
> 첫째, 오래 보게 되는 사진이다. 한 번 보고 넘기지 않고, 계속 들여다보게 되는 것.
> 둘째, 하나의 이야기가 되는 사진이다. 사람, 빛, 색, 장소가 서로 어울려 한 장면이 되는 것.

**17쪽**

> 좋은 사진은 좋은 스타일, 좋은 공간과 같다. 멈추게 하고, 다시 떠오르게 한다.
> *A good picture is like good style and a good space: it makes me stop, and it comes back to me.*

- v1 9쪽의 "생각하게 만들고, 다시 떠오르게 한다" 를 "멈추게 하고" 로 바꿨다 — 책의 동사 "멈춘다" 로 STYLE · PICTURE · ARCHITECTURE 를 한 문장에 묶는다([02_picture.md](02_picture.md) 와 같다).
- 17쪽은 한 문장만 있으면 상자가 비어 보여서 영어 한 줄을 더했다.

## 18–19 · 다리 ②

| 자리 | 전 | 후 |
|---|---|---|
| 18 왼쪽 위 | Grid Exploration 001 | **MOMENT / PLACE** (머리말 — PICTURE 의 MOMENT 에서 ARCHITECTURE 의 PLACE 로 넘어간다). 상자를 본문 앞까지 넓혔다 |
| 18 본문 | A grid system is … | 아래 다리 글 |
| 18 그릴 캡션 | manuscript grids / (single-column layouts) | **Smoke / (September, 5:22 pm)**. 상자가 접힘을 넘어 19쪽 캡션 상자와 겹쳐 있어 18쪽 안으로 줄였다 |
| 19 큰 글자 | A grid system is … (재단선 밖으로) | **Every good picture had a *good place* behind it.** — *good place* 는 마젠타(8–9쪽 풀쿼트의 강조색). 상자 오른쪽 끝을 915 → 811pt(다른 상자와 같은 여백)로 |
| 19 미술관 캡션 | column grids / (multiple vertical columns) | **Gathering / (June, 3:53 pm)** |

**18쪽**

> 좋은 사진을 다시 보면, 늘 그 뒤에 좋은 장소가 있었다. 사람이 멈춘 자리에는 언제나 그 사람을 붙잡아 둔 공간이 있었다.

- "붙잡아 둔 공간" 은 커버의 *A Building That Holds Me* 를 우리말로 옮긴 것이다.
- 19쪽 미술관 사진(그림 앞에 사람들이 모여 멈춰 있다)이 이 문장을 그대로 보여 준다. 그래서 캡션을 *Gathering* 으로 했다.

## 서식

| | 글꼴 |
|---|---|
| 한국어 본문 | AppleGothic Regular 13pt · 행간 20.8pt (A 3쪽 본문과 같다) |
| 영어 질문 제목 | Helvetica Neue Bold 16pt |
| 영어 본문 한 줄 | Helvetica Neue Regular 13pt · 행간 20.8pt |
| 캡션 · 머리말 · 큰 글자 | 원래 상자의 서식 그대로 (16–17: 16pt, 18–19: 14pt, 큰 글자 30pt) |

## 확인할 것 (지원자)

1. **캡션 단어** *Sea · Smoke · Gathering* — 그 사진 앞에서 실제로 멈춘 이유로 고친다. 괄호 안의 달 · 시각은 사진 파일의 촬영 정보에서 읽었다.
2. **바다 사진의 사람 수** — 대체 텍스트는 "한 사람" 이고 v2 기록은 "두 사람" 이었다. 캡션을 사람 수로 고르려면 확인한다.
3. **미술관 사진은 2022년** 사진이다(다른 사진은 2026년 9월). 같은 연출로 묶어도 되는지.
4. 17쪽 영어 한 줄을 남길지.
5. MY PICTURE 한 줄을 넣는다면 사실이 생겼다: 바다 · 그릴 사진은 **23mm f/2** 렌즈, **오후 5시 무렵**. "주로 그렇게 찍는다" 인지는 지원자만 안다.

## 전체 수정 때 맞출 규칙 (이번에 정한 것)

- **머리말**: 섹션 안쪽 펼침은 왼쪽 위에 섹션 이름(STYLE · PICTURE · ARCHITECTURE), 오른쪽 위에 짝 단어(MOOD · MOMENT · PLACE). 다리 펼침은 `MOMENT / PLACE` 처럼 두 짝을 잇는다.
- **번호**: (001)(002)(003) 은 섹션을 여는 펼침에만. 안쪽 지면의 번호는 지운다.
- **캡션**: 굵은 단어 하나(내가 멈춘 이유) + 괄호 안 보통 글씨 한 줄(장소 · 때).
- **본문**: 한국어 AppleGothic 13 / 20.8, 영어 제목 Helvetica Neue Bold 16.
- **강조색**: 다리의 큰 글자에만 마젠타.
- **글 상자는 재단선 안**에(좌우 여백 30.9pt). 사진만 재단선 밖으로 나간다.
- **템플릿 글은 하나도 남기지 않는다**: Template.Systems · Grid Exploration · download now · Series · column/manuscript/modular grids.
